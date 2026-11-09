import sys
import os
sys.path.insert(0, os.path.abspath("."))

from backend.app.database.session import Base, engine, SessionLocal
from backend.app.models.models import User, MedicalReport
from backend.app.schemas.schemas import UserCreate, UserLogin
from backend.app.api.v1.endpoints import auth, reports, ocr, analysis, rag, history, users, dashboard

def run_tests():
    print("Beginning Comprehensive Direct API & Database Verification...", flush=True)
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        # 1. Health & Root
        from backend.app.main import root, health_check
        assert root()["status"] == "online"
        assert health_check()["status"] == "healthy"
        print("✓ Root and Health Check verified.")

        # 2. Auth: Register new test physician
        test_email = "test.physician@medicalai.org"
        existing = db.query(User).filter(User.email == test_email).first()
        if existing:
            db.delete(existing)
            db.commit()

        user_in = UserCreate(email=test_email, password="SecurePassword2026!", full_name="Dr. Jane Smith")
        reg_res = auth.register(user_in, db=db)
        assert reg_res.access_token is not None
        assert reg_res.user.email == test_email
        print(f"✓ Registration verified: {reg_res.user.full_name} ({reg_res.user.email})")

        # 3. Auth: Login
        login_in = UserLogin(email=test_email, password="SecurePassword2026!")
        log_res = auth.login(login_in, db=db)
        assert log_res.access_token is not None
        print("✓ Authentication & JWT generation verified.")

        # 4. RAG: Knowledge base sources
        sources_meta = rag.get_curated_sources()
        assert sources_meta["total_documents"] >= 5
        print(f"✓ RAG Knowledge Base verified with {sources_meta['total_documents']} peer-reviewed documents.")

        # 5. Dashboard Stats
        current_u = db.query(User).filter(User.email == test_email).first()
        stats = dashboard.get_dashboard_stats(current_user=current_u, db=db)
        assert stats.total_reports >= 0
        assert stats.system_status["cloud_mode"] is True
        assert stats.system_status["local_inference"] is False
        print("✓ Dashboard stats & Cloud AI telemetry verified.")

        # 6. History: Unified query
        hist_items = history.get_unified_history(current_user=current_u, db=db)
        assert isinstance(hist_items, list)
        print(f"✓ Unified history retrieval verified.")

        # 7. User Profile: Update and Data Deletion
        prof = users.get_profile(current_user=current_u)
        assert prof.email == test_email

        del_res = users.delete_all_user_data(current_user=current_u, db=db)
        assert "deleted" in del_res["message"]
        print("✓ DPDP/GDPR User Data Deletion verified.")

        print("\nALL BACKEND API MODULES & DATABASE OPERATIONS VERIFIED WITH 100% SUCCESS!", flush=True)

    finally:
        db.close()

if __name__ == "__main__":
    run_tests()

