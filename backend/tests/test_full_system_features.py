import os
import sys
import io
import shutil
from PIL import Image, ImageDraw
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

sys.path.insert(0, os.path.abspath("."))

from backend.app.database.session import Base, engine, SessionLocal
from backend.app.models.models import User, MedicalReport, XrayAnalysis
from backend.app.api.v1.endpoints import dashboard, reports, analysis, history, rag, users, ocr
from backend.app.core.config import settings

def create_sample_lab_pdf(file_path: str):
    """Generate a clean, realistic clinical laboratory report PDF."""
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    c = canvas.Canvas(file_path, pagesize=letter)
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, 750, "METROPOLITAN CLINICAL LABORATORY")
    c.setFont("Helvetica", 10)
    c.drawString(50, 735, "Patient: Test Clinician | Age: 45 | Date: 2026-03-15")
    c.line(50, 725, 550, 725)
    
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, 700, "COMPLETE BLOOD COUNT & METABOLIC PANEL:")
    c.setFont("Helvetica", 10)
    c.drawString(50, 670, "Hemoglobin: 11.2 g/dL (Reference Range: 13.8 - 17.2)")
    c.drawString(50, 650, "White Blood Cells: 14.5 x10^3/uL (Reference Range: 4.5 - 11.0)")
    c.drawString(50, 630, "Platelet Count: 240 x10^3/uL (Reference Range: 150 - 450)")
    c.drawString(50, 610, "Fasting Blood Glucose: 118 mg/dL (Reference Range: 70 - 99)")
    c.drawString(50, 590, "Serum Creatinine: 1.1 mg/dL (Reference Range: 0.6 - 1.3)")
    c.drawString(50, 560, "Clinical Note: Patient reports chronic fatigue and recent mild fever.")
    c.save()

def create_sample_xray_image(file_path: str):
    """Generate a valid synthetic chest radiograph image."""
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    img = Image.new("L", (300, 300), color=50)
    draw = ImageDraw.Draw(img)
    # Draw simulated lung cavities and cardiac silhouette
    draw.ellipse([50, 50, 130, 250], fill=120)
    draw.ellipse([170, 50, 250, 250], fill=120)
    draw.ellipse([110, 120, 190, 240], fill=70)  # Heart
    img.save(file_path, format="PNG")

class MockUploadFile:
    def __init__(self, filename: str, file_path: str, content_type: str = "application/pdf"):
        self.filename = filename
        self.file = open(file_path, "rb")
        self.content_type = content_type

def run_exhaustive_feature_verification():
    print("=" * 80)
    print("COMPREHENSIVE END-TO-END FEATURE VERIFICATION: MEDIEVIDENCE AI")
    print("=" * 80, flush=True)

    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    tmp_dir = "./storage/test_verification_tmp"
    os.makedirs(tmp_dir, exist_ok=True)
    lab_pdf_path = os.path.join(tmp_dir, "sample_blood_test.pdf")
    xray_png_path = os.path.join(tmp_dir, "sample_chest_xray.png")

    try:
        # Create test media
        create_sample_lab_pdf(lab_pdf_path)
        create_sample_xray_image(xray_png_path)
        print("✓ Realistic test artifacts generated (PDF lab report & thoracic radiograph).")

        # ----------------------------------------------------------------------
        # FEATURE 1: Zero-Auth Guest Session / Frictionless Access
        # ----------------------------------------------------------------------
        from backend.app.api.deps import get_current_user
        guest_user = get_current_user(token=None, db=db)
        assert guest_user is not None
        assert guest_user.is_active is True
        print(f"✓ Feature 1 (Zero-Auth Access): Session active for {guest_user.full_name} ({guest_user.email}).")

        # ----------------------------------------------------------------------
        # FEATURE 2: Health & System Telemetry Endpoint
        # ----------------------------------------------------------------------
        from backend.app.main import root, health_check
        r_info = root()
        h_info = health_check()
        assert r_info["status"] == "online"
        assert r_info["architecture"] == "cloud-native"
        assert h_info["status"] == "healthy"
        print("✓ Feature 2 (API Health & Architecture): Cloud-native telemetry operational.")

        # ----------------------------------------------------------------------
        # FEATURE 3: Dashboard Stats & Live Multi-Key Pool Telemetry
        # ----------------------------------------------------------------------
        stats = dashboard.get_dashboard_stats(current_user=guest_user, db=db)
        assert stats.total_reports >= 0
        assert stats.system_status["cloud_mode"] is True
        assert stats.system_status["local_inference"] is False
        assert "llm_provider" in stats.system_status
        print(f"✓ Feature 3 (Dashboard & Telemetry): Status: {stats.system_status['llm_provider']['status']}, Multi-Key Pool: {settings.get_groq_keys().__len__()} keys.")

        # ----------------------------------------------------------------------
        # FEATURE 4: RAG Knowledge Base Retrieval
        # ----------------------------------------------------------------------
        from backend.app.schemas.schemas import RAGQueryRequest
        sources_info = rag.get_curated_sources()
        assert sources_info["total_documents"] >= 5
        rag_query_result = rag.query_medical_rag(RAGQueryRequest(query="Low hemoglobin and high glucose causes", top_k=3))
        assert len(rag_query_result.sources) > 0
        first_ev = rag_query_result.sources[0]
        assert first_ev.source_org and first_ev.source_url
        print(f"✓ Feature 4 (Biomedical RAG): {sources_info['total_documents']} peer-reviewed docs loaded. Top source: {first_ev.source_org} - {first_ev.source_title}.")

        # ----------------------------------------------------------------------
        # FEATURE 5: Real Document Upload & Full Processing Pipeline
        # ----------------------------------------------------------------------
        mock_pdf = MockUploadFile("sample_blood_test.pdf", lab_pdf_path)
        import asyncio
        report_detail = asyncio.run(reports.upload_and_process_report(
            file=mock_pdf,
            report_type="laboratory",
            current_user=guest_user,
            db=db
        ))
        mock_pdf.file.close()

        assert report_detail.id is not None
        assert report_detail.status == "completed"
        assert len(report_detail.extracted_texts) > 0
        assert len(report_detail.medical_entities) >= 3
        
        # Verify exact numerical value preservation
        hb_ent = next((e for e in report_detail.medical_entities if "Hemoglobin" in e.text), None)
        assert hb_ent is not None
        assert hb_ent.normalized_value == "11.2"
        assert hb_ent.flag == "LOW"
        assert hb_ent.is_out_of_range is True

        glu_ent = next((e for e in report_detail.medical_entities if "Glucose" in e.text), None)
        assert glu_ent is not None
        assert glu_ent.normalized_value == "118"
        assert glu_ent.flag == "HIGH"

        # Verify analysis result
        assert len(report_detail.analysis_results) > 0
        analysis_obj = report_detail.analysis_results[0]
        assert len(analysis_obj.summary_text) > 20
        assert len(analysis_obj.patient_friendly_explanation) > 30
        assert len(analysis_obj.doctor_discussion_questions) >= 2
        assert len(analysis_obj.evidence_sources) > 0
        print(f"✓ Feature 5 (Report Analysis Pipeline): Report #{report_detail.id} processed successfully. Preserved values: Hb={hb_ent.normalized_value} ({hb_ent.flag}), Glucose={glu_ent.normalized_value} ({glu_ent.flag}). Model used: {analysis_obj.model_used}.")

        # ----------------------------------------------------------------------
        # FEATURE 6: Download Clinical Report PDF
        # ----------------------------------------------------------------------
        pdf_resp = reports.download_report_pdf(report_id=report_detail.id, current_user=guest_user, db=db)
        assert pdf_resp.path is not None
        assert os.path.exists(pdf_resp.path)
        assert os.path.getsize(pdf_resp.path) > 1000
        print(f"✓ Feature 6 (PDF Export Engine): ReportLab summary generated at {os.path.basename(pdf_resp.path)} ({os.path.getsize(pdf_resp.path)} bytes).")

        # ----------------------------------------------------------------------
        # FEATURE 7: Chest Radiograph Analysis & Quality Evaluation
        # ----------------------------------------------------------------------
        mock_xray = MockUploadFile("sample_chest_xray.png", xray_png_path)
        xray_res = asyncio.run(analysis.analyze_xray_image(
            file=mock_xray,
            current_user=guest_user,
            db=db
        ))
        mock_xray.file.close()

        assert xray_res.id is not None
        assert xray_res.image_quality in ["Good", "Acceptable", "Low Contrast", "Blurry / Low Sharpness"]
        assert "Chest" in xray_res.anatomical_region
        assert xray_res.preliminary_findings is not None
        print(f"✓ Feature 7 (Chest X-ray Analyzer): Study #{xray_res.id} processed. Quality: {xray_res.image_quality}, Region: {xray_res.anatomical_region}, Findings: {xray_res.preliminary_findings[:80]}...")

        # ----------------------------------------------------------------------
        # FEATURE 8: Download Chest X-ray Interpretation PDF
        # ----------------------------------------------------------------------
        xray_pdf = analysis.download_xray_pdf(xray_id=xray_res.id, current_user=guest_user, db=db)
        assert xray_pdf.path is not None
        assert os.path.exists(xray_pdf.path)
        assert os.path.getsize(xray_pdf.path) > 1000
        print(f"✓ Feature 8 (X-ray PDF Generator): Radiograph summary PDF created at {os.path.basename(xray_pdf.path)} ({os.path.getsize(xray_pdf.path)} bytes).")

        # ----------------------------------------------------------------------
        # FEATURE 9: Unified History Search & Filtering
        # ----------------------------------------------------------------------
        all_hist = history.get_unified_history(search=None, report_type=None, current_user=guest_user, db=db)
        assert len(all_hist) >= 2
        
        # Test keyword search filter
        search_hits = history.get_unified_history(search="Hemoglobin", report_type=None, current_user=guest_user, db=db)
        assert len(search_hits) >= 1
        assert any("blood" in h["title"].lower() or "hemoglobin" in str(h.get("summary", "")).lower() for h in search_hits)
        print(f"✓ Feature 9 (History & Search): Found {len(all_hist)} total studies. Keyword filter 'Hemoglobin' matched {len(search_hits)} studies.")

        # ----------------------------------------------------------------------
        # FEATURE 10: Delete Specific Study & DPDP Purge
        # ----------------------------------------------------------------------
        del_item_resp = history.delete_history_item(item_type="xray", item_id=xray_res.id, current_user=guest_user, db=db)
        assert "deleted" in del_item_resp["message"].lower()

        # DPDP purge all data
        purge_resp = users.delete_all_user_data(current_user=guest_user, db=db)
        assert "deleted" in purge_resp["message"].lower()
        
        # Verify database is cleaned
        remaining_reports = db.query(MedicalReport).filter(MedicalReport.user_id == guest_user.id).count()
        remaining_xrays = db.query(XrayAnalysis).filter(XrayAnalysis.user_id == guest_user.id).count()
        assert remaining_reports == 0
        assert remaining_xrays == 0
        print("✓ Feature 10 (Privacy & Data Deletion): DPDP purge verified. 0 residual records remain.")

        print("=" * 80)
        print("ALL 10 CORE FEATURES VERIFIED WITH 100% REAL WORKING FUNCTIONALITY!")
        print("=" * 80, flush=True)

    finally:
        db.close()
        if os.path.exists(tmp_dir):
            shutil.rmtree(tmp_dir, ignore_errors=True)

if __name__ == "__main__":
    run_exhaustive_feature_verification()
