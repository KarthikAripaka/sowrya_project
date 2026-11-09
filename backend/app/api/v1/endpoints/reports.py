import os
import shutil
from typing import List, Optional
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session, joinedload
from backend.app.database.session import get_db
from backend.app.models.models import User, MedicalReport, UploadedFile, ExtractedText, MedicalEntity, AnalysisResult, ActivityLog, EvidenceSource
from backend.app.schemas.schemas import MedicalReportOut, MedicalReportDetailOut
from backend.app.api.deps import get_current_user
from backend.app.ai.ocr.ocr_engine import OCREngine
from backend.app.ai.nlp.medical_nlp import MedicalNLPEngine
from backend.app.ai.rag.rag_pipeline import MedicalRAGPipeline
from backend.app.ai.llm.llm_provider import get_llm_provider
from backend.app.services.pdf_generator import MedicalPDFGenerator

router = APIRouter()
ocr_engine = OCREngine()
nlp_engine = MedicalNLPEngine()
rag_pipeline = MedicalRAGPipeline()
llm_provider = get_llm_provider()
pdf_generator = MedicalPDFGenerator()

@router.post("/upload", response_model=MedicalReportDetailOut)
async def upload_and_process_report(
    title: Optional[str] = Form(None),
    report_type: Optional[str] = Form("laboratory"),
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    upload_dir = f"./storage/uploads/user_{current_user.id}"
    os.makedirs(upload_dir, exist_ok=True)
    file_path = os.path.join(upload_dir, file.filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    file_size = os.path.getsize(file_path)

    clean_title = title if isinstance(title, str) and title.strip() else os.path.splitext(file.filename)[0]
    clean_type = report_type if isinstance(report_type, str) and report_type.strip() else "laboratory"

    report = MedicalReport(
        user_id=current_user.id,
        title=clean_title,
        report_type=clean_type,
        status="processing",
        file_path=file_path,
        original_filename=file.filename,
        file_size=file_size
    )
    db.add(report)
    db.commit()
    db.refresh(report)

    up_file = UploadedFile(
        report_id=report.id,
        filename=file.filename,
        file_path=file_path,
        file_size=file_size,
        mime_type=file.content_type or "application/octet-stream"
    )
    db.add(up_file)

    try:
        # Step 1: Run OCR
        extracted_pages = ocr_engine.extract_text_from_file(file_path)
        all_text = []
        for page_data in extracted_pages:
            ex_rec = ExtractedText(
                report_id=report.id,
                page_number=page_data["page_number"],
                raw_text=page_data["raw_text"],
                ocr_engine=page_data["ocr_engine"],
                confidence_score=page_data.get("confidence_score", 0.95)
            )
            db.add(ex_rec)
            all_text.append(page_data["raw_text"])

        full_document_text = "\n\n".join(all_text)

        # Step 2: Medical NLP & NER
        extracted_entities = []
        for page_data in extracted_pages:
            p_entities = nlp_engine.extract_entities(page_data["raw_text"], page_data["page_number"])
            for ent in p_entities:
                m_ent = MedicalEntity(
                    report_id=report.id,
                    entity_type=ent["entity_type"],
                    text=ent["text"],
                    normalized_value=ent.get("normalized_value"),
                    unit=ent.get("unit"),
                    reference_range=ent.get("reference_range"),
                    is_out_of_range=ent.get("is_out_of_range"),
                    flag=ent.get("flag"),
                    source_page=ent["source_page"],
                    confidence_score=ent.get("confidence_score", 0.95)
                )
                db.add(m_ent)
                extracted_entities.append(ent)

        # Step 3: RAG Evidence Retrieval
        retrieved_evidence = rag_pipeline.retrieve_for_entities(extracted_entities)

        # Step 4: LLM Synthesis with Groq Cloud API
        llm_output = llm_provider.generate_explanation(
            report_text=full_document_text,
            entities=extracted_entities,
            evidence=retrieved_evidence
        )

        # Step 5: Store Analysis Result
        analysis = AnalysisResult(
            report_id=report.id,
            summary_text=llm_output["summary_text"],
            patient_friendly_explanation=llm_output["patient_friendly_explanation"],
            terminology_explanations=llm_output.get("terminology_explanations", []),
            doctor_discussion_questions=llm_output.get("doctor_discussion_questions", []),
            uncertainty_score=llm_output.get("uncertainty_score", 0.05),
            ocr_confidence=0.98,
            extraction_confidence=0.95,
            model_used=llm_output.get("model_used", "Groq llama-3.3-70b-versatile")
        )
        db.add(analysis)
        db.flush()

        # Link evidence sources
        for ev in retrieved_evidence:
            ev_source = EvidenceSource(
                analysis_id=analysis.id,
                source_org=ev.get("source_org", "Official Medical Reference"),
                source_title=ev.get("source_title", "Medical Guidelines"),
                source_url=ev.get("source_url", "https://medlineplus.gov/"),
                excerpt=ev.get("excerpt", "")[:500],
                relevance_score=ev.get("relevance_score", 0.0)
            )
            db.add(ev_source)

        report.status = "completed"
        report.summary = llm_output["summary_text"]
        db.commit()

        # Activity log
        log = ActivityLog(
            user_id=current_user.id,
            action="report_analyzed",
            resource_type="medical_report",
            resource_id=str(report.id),
            details={"filename": file.filename, "entities_count": len(extracted_entities)}
        )
        db.add(log)
        db.commit()

        # Reload with relationships
        full_report = (
            db.query(MedicalReport)
            .options(
                joinedload(MedicalReport.extracted_texts),
                joinedload(MedicalReport.medical_entities),
                joinedload(MedicalReport.analysis_results).joinedload(AnalysisResult.evidence_sources)
            )
            .filter(MedicalReport.id == report.id)
            .first()
        )
        return full_report

    except Exception as e:
        report.status = "failed"
        report.processing_error = str(e)
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing medical report: {str(e)}"
        )


@router.get("", response_model=List[MedicalReportOut])
def list_reports(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return (
        db.query(MedicalReport)
        .filter(MedicalReport.user_id == current_user.id)
        .order_by(MedicalReport.created_at.desc())
        .all()
    )


@router.get("/{report_id}", response_model=MedicalReportDetailOut)
def get_report_detail(
    report_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    report = (
        db.query(MedicalReport)
        .options(
            joinedload(MedicalReport.extracted_texts),
            joinedload(MedicalReport.medical_entities),
            joinedload(MedicalReport.analysis_results).joinedload(AnalysisResult.evidence_sources)
        )
        .filter(MedicalReport.id == report_id, MedicalReport.user_id == current_user.id)
        .first()
    )
    if not report:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Report not found.")
    return report


@router.delete("/{report_id}")
def delete_report(
    report_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    report = db.query(MedicalReport).filter(MedicalReport.id == report_id, MedicalReport.user_id == current_user.id).first()
    if not report:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Report not found.")

    if report.file_path and os.path.exists(report.file_path):
        try:
            os.remove(report.file_path)
        except Exception:
            pass

    db.delete(report)
    db.commit()
    return {"message": "Report and associated records deleted successfully."}


@router.get("/{report_id}/pdf")
def download_report_pdf(
    report_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    report = (
        db.query(MedicalReport)
        .options(
            joinedload(MedicalReport.extracted_texts),
            joinedload(MedicalReport.medical_entities),
            joinedload(MedicalReport.analysis_results).joinedload(AnalysisResult.evidence_sources)
        )
        .filter(MedicalReport.id == report_id, MedicalReport.user_id == current_user.id)
        .first()
    )
    if not report:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Report not found.")

    analysis = report.analysis_results[0] if report.analysis_results else None
    if not analysis:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Analysis not complete for this report.")

    entities_data = [
        {
            "text": e.text,
            "normalized_value": e.normalized_value,
            "unit": e.unit,
            "reference_range": e.reference_range,
            "flag": e.flag,
            "entity_type": e.entity_type
        }
        for e in report.medical_entities
    ]

    analysis_data = {
        "summary_text": analysis.summary_text,
        "patient_friendly_explanation": analysis.patient_friendly_explanation,
        "doctor_discussion_questions": analysis.doctor_discussion_questions or [],
        "extraction_confidence": analysis.extraction_confidence or 0.95,
        "model_used": analysis.model_used
    }

    evidence_sources = [
        {
            "source_title": ev.source_title,
            "source_org": ev.source_org,
            "source_url": ev.source_url,
            "excerpt": ev.excerpt
        }
        for ev in analysis.evidence_sources
    ]

    pdf_path = pdf_generator.generate_report_pdf(
        report_id=report.id,
        report_data={"original_filename": report.original_filename},
        entities=entities_data,
        analysis_data=analysis_data,
        evidence_sources=evidence_sources
    )

    return FileResponse(
        pdf_path,
        media_type="application/pdf",
        filename=os.path.basename(pdf_path)
    )
