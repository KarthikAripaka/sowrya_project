import os
import shutil
from typing import List, Dict, Any
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from backend.app.database.session import get_db
from backend.app.models.models import User, XrayAnalysis, ActivityLog
from backend.app.schemas.schemas import XrayAnalysisOut
from backend.app.api.deps import get_current_user
from backend.app.ai.vision.xray_engine import XrayVisionEngine
from backend.app.services.pdf_generator import MedicalPDFGenerator

router = APIRouter()
xray_engine = XrayVisionEngine()
pdf_generator = MedicalPDFGenerator()

@router.post("/xray", response_model=XrayAnalysisOut)
async def analyze_xray_image(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    upload_dir = f"./storage/uploads/user_{current_user.id}/xrays"
    os.makedirs(upload_dir, exist_ok=True)
    file_path = os.path.join(upload_dir, file.filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        xray_result = xray_engine.analyze_xray(file_path)

        xray_record = XrayAnalysis(
            user_id=current_user.id,
            original_filename=file.filename,
            file_path=file_path,
            image_quality=xray_result.get("image_quality", "Acceptable"),
            anatomical_region=xray_result.get("anatomical_region", "Chest (Thoracic)"),
            model_name=xray_result.get("model_name", "Hosted Medical Imaging API"),
            model_version=xray_result.get("model_version", "Cloud-Adapter-v1"),
            preliminary_findings=xray_result.get("preliminary_findings", ""),
            observations_json=xray_result.get("observations", []),
            uncertainty_info=xray_result.get("uncertainty_info", {}),
            limitations_text=xray_result.get("limitations_text", ""),
            disclaimer=xray_result.get("disclaimer", "")
        )
        db.add(xray_record)
        db.commit()
        db.refresh(xray_record)

        # Activity log
        log = ActivityLog(
            user_id=current_user.id,
            action="xray_analyzed",
            resource_type="xray_analysis",
            resource_id=str(xray_record.id),
            details={"filename": file.filename}
        )
        db.add(log)
        db.commit()

        return xray_record

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"X-ray analysis failed: {str(e)}"
        )


@router.get("/xray", response_model=List[XrayAnalysisOut])
def list_xray_analyses(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return (
        db.query(XrayAnalysis)
        .filter(XrayAnalysis.user_id == current_user.id)
        .order_by(XrayAnalysis.created_at.desc())
        .all()
    )


@router.get("/xray/{xray_id}", response_model=XrayAnalysisOut)
def get_xray_analysis(
    xray_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    xray = db.query(XrayAnalysis).filter(XrayAnalysis.id == xray_id, XrayAnalysis.user_id == current_user.id).first()
    if not xray:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="X-ray study not found.")
    return xray


@router.get("/xray/{xray_id}/pdf")
def download_xray_pdf(
    xray_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    xray = db.query(XrayAnalysis).filter(XrayAnalysis.id == xray_id, XrayAnalysis.user_id == current_user.id).first()
    if not xray:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="X-ray study not found.")

    xray_data = {
        "original_filename": xray.original_filename,
        "preliminary_findings": xray.preliminary_findings,
        "observations_json": xray.observations_json,
        "model_name": xray.model_name,
        "image_quality": xray.image_quality,
        "anatomical_region": xray.anatomical_region,
        "limitations_text": xray.limitations_text
    }

    pdf_path = pdf_generator.generate_xray_pdf(xray.id, xray_data)
    return FileResponse(
        pdf_path,
        media_type="application/pdf",
        filename=os.path.basename(pdf_path)
    )
