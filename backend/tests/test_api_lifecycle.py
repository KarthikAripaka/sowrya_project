import sys
import os
sys.path.insert(0, os.path.abspath("."))

from fastapi.testclient import TestClient
from backend.app.main import app

def test_api():
    client = TestClient(app)
    
    # 1. Root
    res = client.get("/")
    assert res.status_code == 200
    print("✓ GET / response:", res.json()["name"])

    # 2. Health
    res_h = client.get("/api/v1/health")
    assert res_h.status_code == 200
    print("✓ GET /api/v1/health response:", res_h.json()["status"])

    # 3. RAG sources
    res_rag = client.get("/api/v1/rag/sources")
    assert res_rag.status_code == 200
    print("✓ GET /api/v1/rag/sources total documents:", res_rag.json()["total_documents"])

    # 4. Auth login with demo user
    login_res = client.post("/api/v1/auth/login", json={"email": "demo@medicalai.org", "password": "MedicalAI2026!"})
    assert login_res.status_code == 200
    token = login_res.json()["access_token"]
    print("✓ POST /api/v1/auth/login success! Bearer token acquired.")

    # 5. Dashboard stats with auth header
    headers = {"Authorization": f"Bearer {token}"}
    stats_res = client.get("/api/v1/dashboard/stats", headers=headers)
    assert stats_res.status_code == 200
    print("✓ GET /api/v1/dashboard/stats total reports:", stats_res.json()["total_reports"])

    print("ALL API ENDPOINTS TESTED AND VERIFIED PERFECTLY!")

if __name__ == "__main__":
    test_api()
