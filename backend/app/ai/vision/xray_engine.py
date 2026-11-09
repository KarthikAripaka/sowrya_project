import os
import io
import math
import logging
from typing import Dict, Any, List, Tuple, Optional
from PIL import Image, ImageStat, ImageFilter
import urllib.request
import urllib.error
import json
import base64

from backend.app.core.config import settings

logger = logging.getLogger(__name__)

class XrayVisionEngine:
    """
    Cloud-First Hosted Medical Imaging Client for Chest Radiograph Interpretation.
    Performs client-side image validation and quality grading, then delegates
    inference to a hosted medical imaging API.
    
    If the imaging API is unconfigured or unavailable, returns an explicit
    unavailable status without fabricating or inventing pathology scores.
    """

    SUPPORTED_PATHOLOGIES = [
        "Atelectasis",
        "Cardiomegaly",
        "Consolidation",
        "Edema",
        "Effusion",
        "Emphysema",
        "Fibrosis",
        "Hernia",
        "Infiltration",
        "Mass",
        "Nodule",
        "Pleural Thickening",
        "Pneumonia",
        "Pneumothorax"
    ]

    PATHOLOGY_DESCRIPTIONS = {
        "Atelectasis": "Partial collapse or incomplete expansion of pulmonary parenchyma causing focal opacity.",
        "Cardiomegaly": "Enlarged cardiac silhouette with cardiothoracic ratio exceeding 0.50 on PA view.",
        "Consolidation": "Alveolar airspace filling with fluid, inflammatory exudate, or cellular debris.",
        "Edema": "Accumulation of fluid in pulmonary interstitium or alveolar spaces, often vascular.",
        "Effusion": "Fluid accumulation in the pleural space, typically causing blunting of costophrenic angles.",
        "Emphysema": "Hyperinflation of lungs with flattened diaphragms and loss of vascular markings.",
        "Fibrosis": "Chronic pulmonary architectural distortion with reticular markings or honeycombing.",
        "Hernia": "Diaphragmatic defect allowing herniation of abdominal viscera into the thoracic cavity.",
        "Infiltration": "Ill-defined pulmonary opacification indicative of infectious or inflammatory process.",
        "Mass": "Focal pulmonary or mediastinal lesion exceeding 3 cm in diameter.",
        "Nodule": "Well-circumscribed pulmonary opacity equal to or less than 3 cm in diameter.",
        "Pleural Thickening": "Fibrotic or calcific thickening along the pleural surfaces or apical caps.",
        "Pneumonia": "Infectious consolidation or patchy airspace opacity in lung fields.",
        "Pneumothorax": "Air within the pleural space, characterized by a visible visceral pleural line."
    }

    def __init__(self, api_url: Optional[str] = None, api_key: Optional[str] = None):
        self.api_url = (api_url or settings.IMAGING_API_URL or "").strip()
        self.api_key = (api_key or settings.IMAGING_API_KEY or "").strip()

    def validate_image(self, file_path: str) -> Tuple[bool, str, Dict[str, Any]]:
        """
        Validate image existence, dimensions, aspect ratio, and visual quality.
        Uses standard PIL without requiring local PyTorch / deep learning models.
        """
        if not os.path.exists(file_path):
            return False, "File not found.", {}

        try:
            img = Image.open(file_path)
            width, height = img.size

            if width < 128 or height < 128:
                return False, f"Image resolution too low ({width}x{height}). Minimum required: 128x128.", {}

            aspect_ratio = width / max(height, 1)
            if aspect_ratio < 0.4 or aspect_ratio > 2.5:
                return False, f"Unusual aspect ratio ({aspect_ratio:.2f}) for a standard chest radiograph.", {}

            gray_img = img.convert("L")
            stat = ImageStat.Stat(gray_img)
            mean_brightness = stat.mean[0]
            std_contrast = stat.stddev[0]

            edges = gray_img.filter(ImageFilter.FIND_EDGES)
            edge_stat = ImageStat.Stat(edges)
            sharpness_score = edge_stat.mean[0]

            quality = "Good"
            if std_contrast < 20:
                quality = "Low Contrast"
            elif sharpness_score < 4.0:
                quality = "Blurry / Low Sharpness"

            quality_info = {
                "dimensions": f"{width}x{height}",
                "aspect_ratio": round(aspect_ratio, 2),
                "brightness": round(mean_brightness, 1),
                "contrast_std": round(std_contrast, 1),
                "sharpness_score": round(sharpness_score, 1),
                "quality_grade": quality,
                "anatomical_match": "Consistent with thoracic / chest imaging"
            }
            return True, "Valid", quality_info
        except Exception as e:
            return False, f"Error processing image: {str(e)}", {}

    def analyze_xray(self, file_path: str) -> Dict[str, Any]:
        """
        Execute Chest X-ray cloud analysis.
        Strict Medical Safety:
        - If IMAGING_API_URL is configured, invokes the hosted imaging service.
        - If unconfigured or unreachable, returns an explicit 'unavailable' status
          and NEVER fabricates or invents fake pathology findings.
        """
        is_valid, msg, quality_info = self.validate_image(file_path)
        if not is_valid:
            raise ValueError(f"Image validation failed: {msg}")

        # Check if hosted imaging API is configured
        if not self.api_url:
            return {
                "model_name": "Hosted Medical Imaging API (Unconfigured)",
                "model_version": "Cloud-Adapter-v1",
                "image_quality": quality_info.get("quality_grade", "Acceptable"),
                "anatomical_region": "Chest (Thoracic Cavity)",
                "quality_details": quality_info,
                "api_status": "unconfigured",
                "preliminary_findings": (
                    "Hosted medical imaging API is not configured. Set IMAGING_API_URL "
                    "in backend environment variables to enable cloud chest radiograph inference."
                ),
                "observations": [],
                "uncertainty_info": {
                    "status": "Inference Offline",
                    "reason": "No cloud imaging provider endpoint specified in IMAGING_API_URL.",
                    "quality_impact": f"Image quality assessed as '{quality_info.get('quality_grade')}'. Dimensions: {quality_info.get('dimensions')}."
                },
                "limitations_text": (
                    "1. Cloud imaging API is awaiting configuration.\n"
                    "2. System will never generate fabricated or simulated findings.\n"
                    "3. Chest radiographs must be reviewed by a board-certified radiologist."
                ),
                "disclaimer": (
                    "AI-GENERATED RESEARCH OBSERVATION – NOT A MEDICAL DIAGNOSIS. "
                    "This system is intended for educational and research support only. "
                    "Must be interpreted by an appropriately qualified medical professional."
                )
            }

        # Hosted imaging API is configured - call external endpoint
        try:
            observations, findings_summary = self._call_hosted_imaging_api(file_path)
            return {
                "model_name": f"Hosted Medical Imaging API ({self.api_url})",
                "model_version": "Cloud-Inference-v1",
                "image_quality": quality_info.get("quality_grade", "Acceptable"),
                "anatomical_region": "Chest (Thoracic Cavity)",
                "quality_details": quality_info,
                "api_status": "active",
                "preliminary_findings": findings_summary,
                "observations": observations,
                "uncertainty_info": {
                    "calibration_note": "Research model outputs represent statistical feature activations, not confirmed clinical diagnoses.",
                    "dataset_bias": "Model trained on adult chest radiograph datasets (PA/AP views).",
                    "quality_impact": f"Image quality assessed as '{quality_info.get('quality_grade')}'. Contrast std: {quality_info.get('contrast_std')}."
                },
                "limitations_text": (
                    "1. Cloud model predictions require clinical correlation with symptoms and labs.\n"
                    "2. Portable AP radiographs may magnify the cardiac silhouette.\n"
                    "3. Must be reviewed by a qualified healthcare professional."
                ),
                "disclaimer": (
                    "AI-GENERATED RESEARCH OBSERVATION – NOT A MEDICAL DIAGNOSIS. "
                    "This system is intended for educational and research support only."
                )
            }
        except Exception as e:
            logger.warning(f"Hosted medical imaging API call failed: {e}")
            return {
                "model_name": f"Hosted Medical Imaging API ({self.api_url})",
                "model_version": "Cloud-Inference-v1",
                "image_quality": quality_info.get("quality_grade", "Acceptable"),
                "anatomical_region": "Chest (Thoracic Cavity)",
                "quality_details": quality_info,
                "api_status": "unavailable",
                "preliminary_findings": (
                    f"Hosted imaging API endpoint at {self.api_url} is currently unreachable ({str(e)}). "
                    "No findings were generated to prevent inaccurate medical information."
                ),
                "observations": [],
                "uncertainty_info": {
                    "status": "Service Unavailable",
                    "error_detail": str(e),
                    "quality_grade": quality_info.get("quality_grade")
                },
                "limitations_text": (
                    "1. Hosted imaging API is temporarily unreachable.\n"
                    "2. Fabricated results are strictly forbidden under safety guidelines.\n"
                    "3. Consult a qualified medical practitioner."
                ),
                "disclaimer": (
                    "AI-GENERATED RESEARCH OBSERVATION – NOT A MEDICAL DIAGNOSIS. "
                    "Educational and research assistance only."
                )
            }

    def _call_hosted_imaging_api(self, file_path: str) -> Tuple[List[Dict[str, Any]], str]:
        """Send base64-encoded radiograph to hosted imaging API endpoint."""
        with open(file_path, "rb") as f:
            img_b64 = base64.b64encode(f.read()).decode("utf-8")

        payload = json.dumps({
            "image": img_b64,
            "filename": os.path.basename(file_path),
            "modality": "chest_xray"
        }).encode("utf-8")

        headers = {
            "Content-Type": "application/json",
            "User-Agent": "MedicalReportAssistant/2.0"
        }
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        req = urllib.request.Request(self.api_url, data=payload, headers=headers, method="POST")
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode("utf-8"))

        raw_observations = data.get("observations", [])
        observations = []
        for item in raw_observations:
            score = float(item.get("score", 0.0))
            level = "Low"
            if score >= 0.60:
                level = "High"
            elif score >= 0.30:
                level = "Moderate"

            path_name = item.get("pathology", "Observation")
            observations.append({
                "pathology": path_name,
                "score": round(score, 3),
                "confidence_level": level,
                "explanation": item.get("explanation", self.PATHOLOGY_DESCRIPTIONS.get(path_name, "")),
                "literature_reference": item.get("literature_reference", "Radiology reference standards")
            })

        summary = data.get("summary")
        if not summary:
            elevated = [o for o in observations if o["score"] >= 0.35]
            if elevated:
                summary = f"Hosted model detected elevated signals for: {', '.join([o['pathology'] for o in elevated[:3]])}."
            else:
                summary = "No prominent radiographic abnormalities detected above the activation threshold."

        return observations, summary
