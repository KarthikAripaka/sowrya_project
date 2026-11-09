import os
import sys
import httpx
import json
sys.path.insert(0, os.path.abspath("."))
from backend.app.core.config import settings

def test_json_mode():
    key = settings.get_groq_keys()[0]
    headers = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}
    
    payload = {
        "model": "openai/gpt-oss-120b",
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
            content = res.json()['choices'][0]['message']['content']
            print("Content:", content)
            parsed = json.loads(content)
            print("Parsed successfully:", parsed)
            return True
        else:
            print(f"Error: {res.text}")
            return False

if __name__ == "__main__":
    test_json_mode()
