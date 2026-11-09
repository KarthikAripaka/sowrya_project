from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.app.database.session import get_db
from backend.app.models.models import User, MedicalReport, XrayAnalysis, ActivityLog
from backend.app.schemas.schemas import UserOut, UserUpdate
from backend.app.core.security import get_password_hash
from backend.app.api.deps import get_current_user

router = APIRouter()

@router.get("/profile", response_model=UserOut)
def get_profile(current_user: User = Depends(get_current_user)):
    return UserOut.model_validate(current_user)

@router.put("/profile", response_model=UserOut)
def update_profile(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if user_update.full_name is not None:
        current_user.full_name = user_update.full_name
    if user_update.password:
        current_user.hashed_password = get_password_hash(user_update.password)

    db.add(current_user)
    db.commit()
    db.refresh(current_user)
    return UserOut.model_validate(current_user)

@router.delete("/data")
def delete_all_user_data(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    reports = db.query(MedicalReport).filter(MedicalReport.user_id == current_user.id).all()
    for r in reports:
        db.delete(r)

    xrays = db.query(XrayAnalysis).filter(XrayAnalysis.user_id == current_user.id).all()
    for x in xrays:
        db.delete(x)

    logs = db.query(ActivityLog).filter(ActivityLog.user_id == current_user.id).all()
    for l in logs:
        db.delete(l)

    db.commit()
    return {"message": "All personal medical reports, X-rays, and logs have been permanently deleted."}
