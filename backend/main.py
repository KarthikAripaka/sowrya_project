"""
MediEvidence AI ASGI Entrypoint
Exposes the FastAPI application instance from backend.app.main.
"""
from backend.app.main import app

__all__ = ["app"]

