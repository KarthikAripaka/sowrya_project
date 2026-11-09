import os
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from backend.app.core.config import settings
from backend.app.api.v1.api import api_router
from backend.app.database.session import engine, Base, SessionLocal
from backend.app.models.models import User
from backend.app.core.security import get_password_hash

# Ensure directories
os.makedirs("./storage/uploads", exist_ok=True)
os.makedirs("./storage/reports", exist_ok=True)
os.makedirs("./knowledge_base/vector_storage", exist_ok=True)

# Initialize Database Tables
Base.metadata.create_all(bind=engine)

# Seed Demo User
def seed_demo_user():
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == "demo@medicalai.org").first()
        if not user:
            demo_user = User(
                email="demo@medicalai.org",
                hashed_password=get_password_hash("MedicalAI2026!"),
                full_name="Dr. Alex Rivera (Demo User)",
                is_active=True,
                is_superuser=True
            )
            db.add(demo_user)
            db.commit()
    finally:
        db.close()

seed_demo_user()

app = FastAPI(
    title="Evidence-Based Medical AI Assistant API",
    description="Cloud-Native Evidence-Based Medical Report and Chest X-ray Interpretation System using Groq API, Cloud OCR, RAG, and Hosted Vision Inference.",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS Middleware - Support local development, Vercel deployments, and custom cloud domains
origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    settings.FRONTEND_URL,
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_origin_regex=r"^https?://.*",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Centralized Exception Handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "InternalServerError",
            "message": str(exc),
            "disclaimer": settings.MEDICAL_DISCLAIMER
        }
    )

# Include API v1 routes
app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/")
def root():
    return {
        "name": settings.APP_NAME,
        "version": "2.0.0",
        "status": "online",
        "architecture": "cloud-native",
        "llm_provider": settings.LLM_PROVIDER,
        "docs": "/docs",
        "medical_disclaimer": settings.MEDICAL_DISCLAIMER
    }

@app.get("/api/v1/health")
def health_check():
    return {
        "status": "healthy",
        "database": "connected",
        "llm_provider": settings.LLM_PROVIDER,
        "storage": settings.STORAGE_TYPE
    }
