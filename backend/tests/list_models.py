import os
import sys
import httpx
sys.path.insert(0, os.path.abspath("."))
from backend.app.core.config import settings

def list_groq_models():
    key = settings.get_groq_keys()[0]
    headers = {"Authorization": f"Bearer {key}"}
    with httpx.Client(timeout=10.0) as client:
        res = client.get("https://api.groq.com/openai/v1/models", headers=headers)
        if res.status_code == 200:
            models = [m["id"] for m in res.json().get("data", [])]
            print("Available models on Groq for this key:")
            for m in sorted(models):
                print(f"  - {m}")
        else:
            print(f"Error {res.status_code}: {res.text}")

if __name__ == "__main__":
    list_groq_models()

