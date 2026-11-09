import os
from typing import List, Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_ENV: str = "development"
    APP_NAME: str = "Evidence-Based Medical AI Assistant"
    API_V1_STR: str = "/api/v1"
    DEBUG: bool = True
    PORT: int = 8000
    FRONTEND_URL: str = "http://localhost:3000"

    # Security
    JWT_SECRET: str = "medical_ai_assistant_super_secure_secret_key_2026_cloud"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Database (PostgreSQL with pgvector / SQLite development)
    DATABASE_URL: str = "sqlite:///./medical_ai.sqlite"
    USE_PGVECTOR: bool = False

    # Primary Cloud LLM Provider: Groq API
    LLM_PROVIDER: str = "groq"
    GROQ_API_KEY: Optional[str] = None
    GROQ_API_KEYS: Optional[str] = None
    GROQ_MODEL: str = "openai/gpt-oss-120b"
    GROQ_TIMEOUT_SECONDS: int = 45
    GROQ_MAX_REQUESTS_PER_MINUTE: int = 30
    GROQ_API_BASE_URL: str = "https://api.groq.com/openai/v1"

    def get_groq_keys(self) -> List[str]:
        keys = []
        if self.GROQ_API_KEYS:
            for k in self.GROQ_API_KEYS.split(","):
                k_clean = k.strip()
                if k_clean and k_clean not in keys:
                    keys.append(k_clean)
        if self.GROQ_API_KEY:
            k_clean = self.GROQ_API_KEY.strip()
            if k_clean and k_clean not in keys:
                keys.append(k_clean)
        return keys

    # Cloud OCR Provider (Free-tier / Hosted OCR)
    OCR_PROVIDER: str = "cloud_ocr"
    OCR_API_KEY: Optional[str] = None
    OCR_API_URL: str = "https://api.ocr.space/parse/image"
    OCR_SPACE_ENDPOINT: str = "https://api.ocr.space/parse/image"

    # Hosted Medical Imaging Inference API
    IMAGING_PROVIDER: str = "cloud_imaging"
    IMAGING_API_URL: Optional[str] = None
    IMAGING_API_KEY: Optional[str] = None
    IMAGING_MODEL_NAME: str = "CheXNet-DenseNet121-Hosted"
    IMAGING_TIMEOUT_SECONDS: int = 30

    # Hosted Biomedical Embedding Provider
    EMBEDDING_PROVIDER: str = "cloud_embeddings"
    EMBEDDING_API_KEY: Optional[str] = None
    EMBEDDING_API_URL: str = "https://api.groq.com/openai/v1/embeddings"
    EMBEDDING_MODEL_NAME: str = "bge-small-en-v1.5"

    # Cache Configuration
    REDIS_URL: str = "redis://localhost:6379/0"
    USE_REDIS_CACHE: bool = False

    # Cloud Object Storage (S3 / Cloudflare R2 / Local Fallback)
    STORAGE_TYPE: str = "local"  # local or s3
    STORAGE_DIR: str = "./storage"
    S3_BUCKET_NAME: Optional[str] = None
    S3_ENDPOINT_URL: Optional[str] = None
    S3_ACCESS_KEY: Optional[str] = None
    S3_SECRET_KEY: Optional[str] = None
    S3_REGION: str = "us-east-1"
    MAX_UPLOAD_SIZE_MB: int = 25

    # Medical Safety & Disclaimer
    MEDICAL_DISCLAIMER: str = (
        "AI-GENERATED EDUCATIONAL SUMMARY – NOT A MEDICAL DIAGNOSIS. "
        "Consult a qualified healthcare professional for medical advice."
    )

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


settings = Settings()
