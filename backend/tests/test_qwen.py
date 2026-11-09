import os
import sys
import httpx
import json
sys.path.insert(0, os.path.abspath("."))
from backend.app.core.config import settings

def test_qwen():
    key = settings.get_groq_keys()[0]
    headers = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}
    
    payload = {
        "model": "qwen/qwen3.8-27b",
        "messages": [
            {"role": "system", "content": "You are a clinical AI. Output a valid JSON object with keys 'summary' and 'doctor_questions'."},
            {"role": "user", "content": "Hemoglobin is 11.2 g/dL."}
        ],
        "response_format": {"type": "json_object"},
        "max_tokens": 1000
    }
    with httpx.Client(timeout=15.0) as client:
        res = client.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=payload)
        print(f"HTTP {res.status_code}")
        if res.status_code == 200:
            print("Content:", res.json()['choices'][0]['message']['content'])
            return True
        else:
            print(f"Error: {res.text}")
            return False

if __name__ == "__main__":
    test_qwen()

