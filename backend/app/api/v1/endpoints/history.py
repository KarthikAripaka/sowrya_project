from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session
from backend.app.database.session import get_db
from backend.app.models.models import User, MedicalReport, XrayAnalysis
from backend.app.api.deps import get_current_user

router = APIRouter()

@router.get("")
def get_unified_history(
    search: Optional[str] = Query(None),
    report_type: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    items = []

    # Clean filter values
    search_str = search if isinstance(search, str) else None
    rtype_str = report_type if isinstance(report_type, str) else None

    # Fetch medical reports
    rep_query = db.query(MedicalReport).filter(MedicalReport.user_id == current_user.id)
    if rtype_str and rtype_str != "all" and rtype_str != "xray":
        rep_query = rep_query.filter(MedicalReport.report_type == rtype_str)
    
    reports = rep_query.order_by(MedicalReport.created_at.desc()).all()

    for r in reports:
        if search_str:
            s_low = search_str.lower()
            in_title = s_low in (r.title or "").lower()
            in_fname = s_low in (r.original_filename or "").lower()
            in_summary = s_low in (r.summary or "").lower()
            if not (in_title or in_fname or in_summary):
                continue
        items.append({
            "id": r.id,
            "type": "report",
            "title": r.title,
            "filename": r.original_filename,
            "category": r.report_type,
            "status": r.status,
            "summary": r.summary,
            "created_at": r.created_at
        })

    # Fetch X-rays
    if not rtype_str or rtype_str in ["all", "xray", "radiology"]:
        xray_query = db.query(XrayAnalysis).filter(XrayAnalysis.user_id == current_user.id)
        xrays = xray_query.order_by(XrayAnalysis.created_at.desc()).all()

        for x in xrays:
            if search_str and search_str.lower() not in x.original_filename.lower() and search_str.lower() not in x.preliminary_findings.lower():
                continue
            items.append({
                "id": x.id,
                "type": "xray",
                "title": f"Chest Radiograph ({x.original_filename})",
                "filename": x.original_filename,
                "category": "radiology",
                "status": "completed",
                "summary": x.preliminary_findings,
                "created_at": x.created_at
            })

    items.sort(key=lambda x: x["created_at"], reverse=True)
    return items


@router.delete("/{item_type}/{item_id}")
def delete_history_item(
    item_type: str,
    item_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if item_type == "report":
        report = db.query(MedicalReport).filter(MedicalReport.id == item_id, MedicalReport.user_id == current_user.id).first()
        if not report:
            raise HTTPException(status_code=404, detail="Report not found.")
        db.delete(report)
        db.commit()
        return {"message": "Report deleted."}
    elif item_type == "xray":
        xray = db.query(XrayAnalysis).filter(XrayAnalysis.id == item_id, XrayAnalysis.user_id == current_user.id).first()
        if not xray:
            raise HTTPException(status_code=404, detail="X-ray study not found.")
        db.delete(xray)
        db.commit()
        return {"message": "X-ray study deleted."}
    else:
        raise HTTPException(status_code=400, detail="Invalid item type.")
