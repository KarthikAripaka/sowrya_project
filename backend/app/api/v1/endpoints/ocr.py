import os
import shutil
from fastapi import APIRouter, UploadFile, File, HTTPException, status
from backend.app.ai.ocr.ocr_engine import OCREngine

router = APIRouter()
ocr_engine = OCREngine()

@router.post("/extract")
async def extract_ocr(file: UploadFile = File(...)):
    """
    Direct OCR endpoint: Upload any PDF, JPG, or PNG and retrieve extracted text with page tracking.
    """
    temp_dir = "./storage/uploads/temp"
    os.makedirs(temp_dir, exist_ok=True)
    temp_path = os.path.join(temp_dir, file.filename)

    try:
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        pages = ocr_engine.extract_text_from_file(temp_path)
        return {
            "filename": file.filename,
            "total_pages": len(pages),
            "pages": pages
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"OCR processing failed: {str(e)}"
        )
    finally:
        if os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except Exception:
                pass

