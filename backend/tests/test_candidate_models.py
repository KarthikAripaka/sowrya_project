import os
import sys
import httpx
sys.path.insert(0, os.path.abspath("."))
from backend.app.core.config import settings

def test_models():
    key = settings.get_groq_keys()[0]
    headers = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}
    
    candidates = ["openai/gpt-oss-120b", "openai/gpt-oss-20b", "qwen/qwen3.8-27b"]
    for m in candidates:
        payload = {
            "model": m,
            "messages": [{"role": "user", "content": "Explain in one sentence what a hemoglobin level of 11.2 g/dL indicates."}],
            "max_tokens": 100
        }
        with httpx.Client(timeout=10.0) as client:
            res = client.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=payload)
            print(f"Model {m}: HTTP {res.status_code}")
            if res.status_code == 200:
                print(f"  Response: {res.json()['choices'][0]['message']['content'].strip()}")
                return m
            else:
                print(f"  Error: {res.text}")
    return None

if __name__ == "__main__":
    working_model = test_models()
    print(f"\nBest working model: {working_model}")

