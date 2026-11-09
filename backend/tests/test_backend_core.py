import os
import sys
sys.path.insert(0, os.path.abspath("."))
import pytest
import asyncio
from unittest.mock import patch, MagicMock
from PIL import Image

from backend.app.core.security import get_password_hash, verify_password, create_access_token, decode_token
from backend.app.ai.ocr.ocr_engine import OCREngine
from backend.app.ai.nlp.medical_nlp import MedicalNLPEngine
from backend.app.ai.rag.rag_pipeline import MedicalRAGPipeline
from backend.app.ai.vision.xray_engine import XrayVisionEngine
from backend.app.ai.llm.llm_provider import GroqProvider, get_llm_provider
from backend.app.services.pdf_generator import MedicalPDFGenerator


def test_security_password_hashing():
    pw = "SuperSecretMed123!"
    hashed = get_password_hash(pw)
    assert verify_password(pw, hashed) is True
    assert verify_password("WrongPassword", hashed) is False


def test_jwt_token_creation_and_decode():
    token = create_access_token(subject=42)
    payload = decode_token(token)
    assert payload is not None
    assert payload["sub"] == "42"


def test_medical_nlp_extraction():
    nlp = MedicalNLPEngine()
    sample_text = (
        "COMPLETE BLOOD COUNT:\n"
        "Hemoglobin: 11.2 g/dL (Reference: 13.8 - 17.2)\n"
        "White Blood Cells: 14.5 x10^3/uL (Reference: 4.5 - 11.0)\n"
        "Platelet Count: 240 x10^3/uL (Reference: 150 - 450)\n"
        "Patient presents with fatigue and suspected pneumonia."
    )
    entities = nlp.extract_entities(sample_text, page_number=1)
    
    hb = next((e for e in entities if e["text"] == "Hemoglobin"), None)
    assert hb is not None
    assert hb["normalized_value"] == "11.2"
    assert hb["flag"] == "LOW"

    wbc = next((e for e in entities if e["text"] == "White Blood Cell Count"), None)
    assert wbc is not None
    assert wbc["normalized_value"] == "14.5"
    assert wbc["flag"] == "HIGH"

    pneumonia = next((e for e in entities if e["text"] == "Pneumonia"), None)
    assert pneumonia is not None
    assert pneumonia["entity_type"] == "disease"


def test_rag_evidence_retrieval():
    rag = MedicalRAGPipeline()
    results = rag.retrieve_evidence("Low hemoglobin anemia causes", top_k=2)
    assert len(results) > 0
    assert any("Hemoglobin" in r["source_title"] or "MedlinePlus" in r["source_org"] for r in results)


def test_groq_provider_initialization():
    provider = get_llm_provider()
    assert isinstance(provider, GroqProvider)
    assert bool(provider.model)
    assert provider.provider_name == "Groq"


def test_groq_provider_missing_key():
    provider = GroqProvider(api_key="")
    health = provider.check_health()
    assert health["status"] in ["awaiting_configuration", "awaiting_api_key"]
    assert "GROQ_API_KEY" in health["message"]


def test_groq_provider_invalid_key_handling():
    """Test that an invalid Groq API key returns a clear unauthorized error rather than crashing."""
    provider = GroqProvider(api_key="gsk_invalid_test_key_abc123")
    mock_resp = MagicMock()
    mock_resp.status_code = 401
    mock_resp.text = "Invalid API Key"
    
    with patch("httpx.Client.get", return_value=mock_resp):
        health = provider.check_health()
        assert health["status"] == "unauthorized"
        assert "invalid" in health["message"].lower()


def test_groq_provider_rate_limit_handling():
    """Test simulated HTTP 429 rate limit response."""
    provider = GroqProvider(api_key="gsk_valid_mock_key")
    
    mock_response = MagicMock()
    mock_response.status_code = 429
    mock_response.json.return_value = {
        "error": {
            "message": "Rate limit exceeded. Please wait before submitting more requests.",
            "type": "tokens",
            "code": "rate_limit_exceeded"
        }
    }
    
    with patch("httpx.Client.get", return_value=mock_response):
        health = provider.check_health()
        assert health["status"] == "rate_limited"
        assert "rate limit" in health["message"].lower() or "limit" in health["message"].lower()


def test_groq_provider_multi_key_rotation_on_429():
    """
    Test Multi-Key Failover Pool:
    When key 1 returns HTTP 429, the provider rotates automatically to key 2.
    If key 2 succeeds, the caller receives the generated output seamlessly.
    """
    import json
    keys = ["gsk_key1_mock", "gsk_key2_mock", "gsk_key3_mock"]
    provider = GroqProvider(api_keys=keys)
    assert len(provider.api_keys) == 3
    assert provider.api_key == "gsk_key1_mock"
    
    mock_resp_429 = MagicMock()
    mock_resp_429.status_code = 429
    mock_resp_429.text = "Rate limit reached on key 1"
    
    mock_resp_200 = MagicMock()
    mock_resp_200.status_code = 200
    mock_resp_200.json.return_value = {
        "choices": [{
            "message": {
                "content": json.dumps({
                    "summary": "Multi-key rotation successfully responded on key 2.",
                    "patient_explanation": "All tests normal.",
                    "terminology": [],
                    "doctor_questions": ["What is my next step?"],
                    "uncertainty_note": "Calibrated"
                })
            }
        }]
    }
    
    with patch("httpx.Client.post", side_effect=[mock_resp_429, mock_resp_200]):
        output = provider.generate_explanation(
            report_text="Hemoglobin 14.0 g/dL",
            entities=[],
            evidence=[]
        )
        assert "Key #2" in output["model_used"] or "Key #2/3" in output["model_used"]
        assert "Multi-key rotation successfully responded on key 2" in output["summary_text"]
        assert provider.api_key == "gsk_key2_mock"


def test_missing_imaging_api_configuration():
    """
    Test Medical Safety Rule:
    When IMAGING_API_URL is unconfigured, the system MUST return explicit unavailable
    status and NEVER invent or simulate fake X-ray pathology findings.
    """
    os.makedirs("./storage/test_tmp", exist_ok=True)
    test_img_path = "./storage/test_tmp/sample_test_xray.png"
    
    # Create valid synthetic grayscale test image (256x256)
    img = Image.new("L", (256, 256), color=128)
    img.save(test_img_path)
    
    try:
        engine = XrayVisionEngine(api_url="")
        res = engine.analyze_xray(test_img_path)
        
        assert res["api_status"] == "unconfigured"
        assert len(res["observations"]) == 0  # CRITICAL: Must NEVER invent findings
        assert "not configured" in res["preliminary_findings"].lower()
        assert "IMAGING_API_URL" in res["preliminary_findings"]
    finally:
        if os.path.exists(test_img_path):
            os.remove(test_img_path)


def test_cloud_ocr_file_validation():
    ocr = OCREngine()
    valid, msg = ocr.validate_file("non_existent_file.pdf")
    assert valid is False

    # Test empty file
    os.makedirs("./storage/test_tmp", exist_ok=True)
    empty_path = "./storage/test_tmp/empty_test.pdf"
    with open(empty_path, "wb") as f:
        pass
    
    try:
        valid, msg = ocr.validate_file(empty_path)
        assert valid is False
        assert "empty" in msg.lower()
    finally:
        if os.path.exists(empty_path):
            os.remove(empty_path)


if __name__ == "__main__":
    print("Running comprehensive core test suite...\n")
    test_security_password_hashing()
    print("✓ Security password hashing verified.")
    test_jwt_token_creation_and_decode()
    print("✓ JWT token creation & decoding verified.")
    test_medical_nlp_extraction()
    print("✓ Medical NLP & entity preservation verified.")
    test_rag_evidence_retrieval()
    print("✓ RAG medical evidence retrieval verified.")
    test_groq_provider_initialization()
    print("✓ GroqProvider initialization verified.")
    test_groq_provider_missing_key()
    print("✓ GroqProvider missing key handling verified.")
    test_groq_provider_invalid_key_handling()
    print("✓ GroqProvider invalid key error handling verified.")
    test_groq_provider_rate_limit_handling()
    print("✓ GroqProvider rate limit (HTTP 429) handling verified.")
    test_groq_provider_multi_key_rotation_on_429()
    print("✓ GroqProvider multi-key automatic failover pool on 429 verified.")
    test_missing_imaging_api_configuration()
    print("✓ Missing imaging API safety verified (never invents fake findings).")
    test_cloud_ocr_file_validation()
    print("✓ Cloud OCR file validation verified.")
    print("\nALL 11 CORE AI & SECURITY TESTS PASSED WITH 100% SUCCESS!")
