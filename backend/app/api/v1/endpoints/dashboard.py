from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.app.database.session import get_db
from backend.app.models.models import User, MedicalReport, XrayAnalysis
from backend.app.schemas.schemas import DashboardStatsOut, MedicalReportOut, XrayAnalysisOut
from backend.app.api.deps import get_current_user
from backend.app.ai.llm.llm_provider import get_llm_provider
from backend.app.core.config import settings

router = APIRouter()
llm_provider = get_llm_provider()

@router.get("/stats", response_model=DashboardStatsOut)
def get_dashboard_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    all_reports = (
        db.query(MedicalReport)
        .filter(MedicalReport.user_id == current_user.id)
        .order_by(MedicalReport.created_at.desc())
        .all()
    )
    total_reports = len(all_reports)
    completed_reports = sum(1 for r in all_reports if r.status == "completed")
    pending_reports = sum(1 for r in all_reports if r.status in ["pending", "processing"])

    all_xrays = (
        db.query(XrayAnalysis)
        .filter(XrayAnalysis.user_id == current_user.id)
        .order_by(XrayAnalysis.created_at.desc())
        .all()
    )
    total_xrays = len(all_xrays)

    cloud_llm_health = llm_provider.check_health()

    imaging_status = "active" if (settings.IMAGING_API_URL and settings.IMAGING_API_URL.strip()) else "awaiting_configuration"

    system_status = {
        "llm_provider": cloud_llm_health,
        "ocr_engine": "Cloud OCR (Groq Vision / PyPDF) Active",
        "vision_ai": f"Hosted Medical Imaging API ({imaging_status})",
        "vector_db": "pgvector & Cloud Vector Index Active",
        "cloud_mode": True,
        "local_inference": False
    }

    return DashboardStatsOut(
        total_reports=total_reports,
        total_xrays=total_xrays,
        completed_analyses=completed_reports + total_xrays,
        pending_analyses=pending_reports,
        recent_reports=[MedicalReportOut.model_validate(r) for r in all_reports[:4]],
        recent_xrays=[XrayAnalysisOut.model_validate(x) for x in all_xrays[:4]],
        system_status=system_status
    )
