from fastapi import APIRouter
from backend.app.api.v1.endpoints import auth, reports, ocr, analysis, rag, history, users, dashboard

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(reports.router, prefix="/reports", tags=["Medical Reports"])
api_router.include_router(ocr.router, prefix="/ocr", tags=["OCR Extraction"])
api_router.include_router(analysis.router, prefix="/analysis", tags=["Medical & X-ray Analysis"])
api_router.include_router(rag.router, prefix="/rag", tags=["RAG & Knowledge Retrieval"])
api_router.include_router(history.router, prefix="/history", tags=["Analysis History"])
api_router.include_router(users.router, prefix="/users", tags=["User & Profile Management"])
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["Dashboard"])

