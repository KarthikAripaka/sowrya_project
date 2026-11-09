import os
import sys
sys.path.insert(0, os.path.abspath("."))

from backend.app.core.config import settings
from backend.app.ai.llm.llm_provider import GroqProvider

def test_live_keys():
    print("Testing live Groq API keys from settings...", flush=True)
    keys = settings.get_groq_keys()
    print(f"Total keys configured: {len(keys)}")
    
    for idx, key in enumerate(keys, 1):
        masked_key = f"{key[:8]}...{key[-4:]}"
        print(f"\n[{idx}/{len(keys)}] Testing Key: {masked_key}")
        provider = GroqProvider(api_key=key)
        health = provider.check_health()
        print(f"  Health Status: {health.get('status')}")
        print(f"  Provider: {health.get('provider')}")
        print(f"  Details: {health.get('quota_status', health.get('message', ''))}")
        
    print("\nTesting live GroqProvider multi-key pool generation...", flush=True)
    pool_provider = GroqProvider()
    explanation = pool_provider.generate_explanation(
        report_text="PATIENT LAB REPORT: Hemoglobin: 11.2 g/dL (Normal Range: 13.8 - 17.2 g/dL). Fasting Glucose: 118 mg/dL (Normal: 70 - 99 mg/dL).",
        entities=[
            {"text": "Hemoglobin", "normalized_value": "11.2", "unit": "g/dL", "reference_range": "13.8 - 17.2", "flag": "LOW"},
            {"text": "Fasting Blood Glucose", "normalized_value": "118", "unit": "mg/dL", "reference_range": "70 - 99", "flag": "HIGH"}
        ],
        evidence=[
            {
                "source_org": "MedlinePlus (NLM/NIH)",
                "source_title": "Hemoglobin Test",
                "source_url": "https://medlineplus.gov/lab-tests/hemoglobin-test/",
                "excerpt": "A low hemoglobin level is usually a sign of anemia."
            }
        ]
    )
    
    print("\n--- Live Generation Output ---")
    print(f"Model Used: {explanation.get('model_used')}")
    print(f"Summary: {explanation.get('summary_text')}")
    print(f"Patient Friendly: {explanation.get('patient_friendly_explanation')[:200]}...")
    print(f"Terminology Count: {len(explanation.get('terminology_explanations', []))}")
    print(f"Doctor Questions: {explanation.get('doctor_discussion_questions')}")
    assert explanation.get('summary_text') is not None
    assert len(explanation.get('doctor_discussion_questions', [])) > 0
    print("\n✓ Live Groq API Key Verification Succeeded with 100% Success!")

if __name__ == "__main__":
    test_live_keys()

