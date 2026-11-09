import os
import re
import io
import json
import base64
import logging
import urllib.request
import urllib.parse
import urllib.error
from typing import List, Dict, Any, Optional, Tuple
from PIL import Image
import pypdf

from backend.app.core.config import settings

logger = logging.getLogger(__name__)

class OCREngine:
    """
    Cloud-First Medical Document OCR Pipeline.
    Supports digital PDFs, scanned PDFs, JPG, PNG, and JPEG.
    
    1. Digital PDFs: Extracted via pypdf (instant, lossless text, preserved numerical precision).
    2. Scanned PDFs & Images: Processed via Groq Vision Cloud API (Llama 3.2 Vision)
       or OCR.space Cloud API.
    Zero local GPU or local AI model weights required.
    """

    def __init__(self):
        self.groq_api_keys = settings.get_groq_keys()
        self.groq_api_key = self.groq_api_keys[0] if self.groq_api_keys else ""
        self.ocr_provider = (settings.OCR_PROVIDER or "groq_vision").lower()
        self.ocr_api_key = (settings.OCR_API_KEY or "").strip()
        self.ocr_api_url = (settings.OCR_API_URL or "").strip()

    def validate_file(self, file_path: str) -> Tuple[bool, str]:
        """Validate file existence, size, and extension."""
        if not os.path.exists(file_path):
            return False, "File does not exist."
        
        file_size = os.path.getsize(file_path)
        if file_size == 0:
            return False, "File is empty (0 bytes)."
        
        max_size = 25 * 1024 * 1024  # 25 MB
        if file_size > max_size:
            return False, f"File exceeds maximum allowed size of 25MB (size: {file_size / (1024*1024):.1f}MB)."
            
        ext = os.path.splitext(file_path)[1].lower()
        allowed = [".pdf", ".jpg", ".jpeg", ".png", ".tiff", ".bmp"]
        if ext not in allowed:
            return False, f"Unsupported file extension '{ext}'. Allowed: {', '.join(allowed)}."

        return True, "Valid"

    def extract_text_from_file(self, file_path: str) -> List[Dict[str, Any]]:
        """
        Extract text page by page with full traceability.
        Returns list of dicts: [{'page_number': 1, 'raw_text': '...', 'ocr_engine': '...', 'confidence_score': 0.95, 'is_scanned': False}]
        """
        is_valid, msg = self.validate_file(file_path)
        if not is_valid:
            raise ValueError(f"File validation error: {msg}")

        ext = os.path.splitext(file_path)[1].lower()
        if ext == ".pdf":
            return self._extract_from_pdf(file_path)
        else:
            return self._extract_from_image(file_path)

    def _extract_from_pdf(self, pdf_path: str) -> List[Dict[str, Any]]:
        results = []
        try:
            reader = pypdf.PdfReader(pdf_path)
            total_pages = len(reader.pages)

            for idx, page in enumerate(reader.pages):
                page_num = idx + 1
                text = page.extract_text() or ""
                
                # If digital text exists and is meaningful
                if len(text.strip()) > 30:
                    results.append({
                        "page_number": page_num,
                        "raw_text": text.strip(),
                        "ocr_engine": "pypdf-digital-extract",
                        "confidence_score": 0.99,
                        "is_scanned": False
                    })
                else:
                    # PDF page is scanned or contains embedded image elements
                    page_img_text, conf, engine = self._extract_scanned_pdf_page(page, page_num)
                    results.append({
                        "page_number": page_num,
                        "raw_text": page_img_text.strip(),
                        "ocr_engine": engine,
                        "confidence_score": conf,
                        "is_scanned": True
                    })
        except Exception as e:
            results.append({
                "page_number": 1,
                "raw_text": f"Error parsing PDF document: {str(e)}",
                "ocr_engine": "error-fallback",
                "confidence_score": 0.0,
                "is_scanned": False
            })

        return results

    def _extract_scanned_pdf_page(self, page, page_num: int) -> Tuple[str, float, str]:
        """Extract image from PDF page and send to cloud OCR."""
        try:
            for image_file_object in page.images:
                img = Image.open(io.BytesIO(image_file_object.data))
                text, conf, engine = self._ocr_image(img)
                if text:
                    return text, conf, engine
        except Exception as e:
            logger.warning(f"Error extracting image from PDF page {page_num}: {e}")

        return f"[Scanned page {page_num}: No readable digital text stream]", 0.70, "cloud-ocr-pending"

    def _extract_from_image(self, image_path: str) -> List[Dict[str, Any]]:
        img = Image.open(image_path)
        text, conf, engine = self._ocr_image(img)
        return [{
            "page_number": 1,
            "raw_text": text,
            "ocr_engine": engine,
            "confidence_score": conf,
            "is_scanned": True
        }]

    def _ocr_image(self, img: Image.Image) -> Tuple[str, float, str]:
        """
        Run cloud OCR on a PIL image.
        Tries:
        1. Groq Vision Cloud API if GROQ_API_KEY is configured.
        2. OCR.space free API if OCR_API_KEY is configured.
        3. Clear guidance if no cloud OCR credentials configured.
        """
        # Save image to in-memory bytes
        buf = io.BytesIO()
        img.convert("RGB").save(buf, format="JPEG", quality=85)
        img_bytes = buf.getvalue()
        b64_img = base64.b64encode(img_bytes).decode("utf-8")

        # 1. Cloud Groq Vision OCR
        if self.groq_api_key:
            try:
                text = self._call_groq_vision(b64_img)
                if text:
                    return text, 0.95, "groq-vision-llama-3.2-11b"
            except Exception as e:
                logger.warning(f"Groq Vision OCR call failed: {e}")

        # 2. OCR.space Free Cloud OCR
        if self.ocr_api_key:
            try:
                text = self._call_ocr_space(img_bytes)
                if text:
                    return text, 0.92, "ocr-space-cloud"
            except Exception as e:
                logger.warning(f"OCR.space call failed: {e}")

        # 3. Transparent unconfigured notice
        return (
            "Medical document image received. Cloud OCR requires GROQ_API_KEY "
            "or OCR_API_KEY in backend .env to transcribe scanned raster images. "
            "Digital PDF reports with embedded text can be processed without external keys."
        ), 0.70, "cloud-ocr-awaiting-config"

    def _call_groq_vision(self, b64_img: str) -> Optional[str]:
        """Call Groq Llama 3.2 Vision model to transcribe document image verbatim with key rotation."""
        from groq import Groq
        keys_to_try = self.groq_api_keys or ([self.groq_api_key] if self.groq_api_key else [])
        
        for key in keys_to_try:
            try:
                client = Groq(api_key=key, timeout=20.0)
                response = client.chat.completions.create(
                    model="llama-3.2-11b-vision-preview",
                    messages=[
                        {
                            "role": "user",
                            "content": [
                                {
                                    "type": "text",
                                    "text": (
                                        "Transcribe all text from this medical report image verbatim. "
                                        "Preserve all laboratory test names, numbers, units, and reference intervals exactly as shown. "
                                        "Do not summarize or invent any text."
                                    )
                                },
                                {
                                    "type": "image_url",
                                    "image_url": {
                                        "url": f"data:image/jpeg;base64,{b64_img}"
                                    }
                                }
                            ]
                        }
                    ],
                    temperature=0.0,
                    max_tokens=2048
                )
                text = response.choices[0].message.content.strip()
                if text:
                    return text
            except Exception as e:
                logger.warning(f"Groq Vision OCR attempt with key {key[:10]}... failed: {e}. Trying next key...")
                continue
        return None

    def _call_ocr_space(self, img_bytes: bytes) -> Optional[str]:
        """Call OCR.space Free REST API."""
        url = "https://api.ocr.space/parse/image"
        b64_data = "data:image/jpeg;base64," + base64.b64encode(img_bytes).decode("utf-8")
        data = urllib.parse.urlencode({
            "apikey": self.ocr_api_key,
            "base64Image": b64_data,
            "language": "eng",
            "isOverlayRequired": False,
            "detectOrientation": True,
            "scale": True,
            "OCREngine": 2
        }).encode("utf-8")

        req = urllib.request.Request(url, data=data, method="POST")
        with urllib.request.urlopen(req, timeout=15) as resp:
            res_json = json.loads(resp.read().decode("utf-8"))
            parsed_results = res_json.get("ParsedResults", [])
            if parsed_results:
                return parsed_results[0].get("ParsedText", "").strip()
        return None

# Alias for backward compatibility
CloudOCREngine = OCREngine
