from typing import List, Optional, Dict, Any
from pydantic import BaseModel, EmailStr, Field
import datetime

# --- AUTH & USER SCHEMAS ---
class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None

class UserCreate(UserBase):
    password: str = Field(..., min_length=6)

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    password: Optional[str] = Field(None, min_length=6)

class UserOut(UserBase):
    id: int
    is_active: bool
    is_superuser: bool
    created_at: datetime.datetime

    class Config:
        from_attributes = True

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut

# --- MEDICAL ENTITY SCHEMAS ---
class MedicalEntityBase(BaseModel):
    entity_type: str
    text: str
    normalized_value: Optional[str] = None
    unit: Optional[str] = None
    reference_range: Optional[str] = None
    is_out_of_range: Optional[bool] = None
    flag: Optional[str] = None  # LOW, NORMAL, HIGH, CRITICAL
    source_page: int = 1
    confidence_score: Optional[float] = None

class MedicalEntityCreate(MedicalEntityBase):
    report_id: int

class MedicalEntityOut(MedicalEntityBase):
    id: int
    created_at: datetime.datetime

    class Config:
        from_attributes = True

# --- EXTRACTED TEXT SCHEMAS ---
class ExtractedTextOut(BaseModel):
    id: int
    page_number: int
    raw_text: str
    ocr_engine: str
    confidence_score: Optional[float] = None
    created_at: datetime.datetime

    class Config:
        from_attributes = True

# --- EVIDENCE & RAG SCHEMAS ---
class EvidenceSourceOut(BaseModel):
    id: Optional[int] = None
    source_org: str
    source_title: str
    source_url: str
    excerpt: str
    relevance_score: float = 0.0

    class Config:
        from_attributes = True

class RAGQueryRequest(BaseModel):
    query: str
    top_k: int = 4
    category: Optional[str] = None

class RAGQueryResponse(BaseModel):
    query: str
    sources: List[EvidenceSourceOut]
    retrieved_count: int

# --- ANALYSIS SCHEMAS ---
class TerminologyItem(BaseModel):
    term: str
    plain_english_explanation: str
    clinical_context: Optional[str] = None

class LabResultItem(BaseModel):
    test_name: str
    value: str
    unit: Optional[str] = None
    reference_range: Optional[str] = None
    status: str = "NORMAL"  # LOW, NORMAL, HIGH, UNKNOWN
    explanation: str
    source: Optional[str] = None

class AnalysisResultOut(BaseModel):
    id: int
    report_id: int
    summary_text: str
    patient_friendly_explanation: str
    terminology_explanations: Optional[List[Dict[str, Any]]] = None
    doctor_discussion_questions: Optional[List[str]] = None
    uncertainty_score: float
    ocr_confidence: Optional[float] = None
    extraction_confidence: Optional[float] = None
    model_used: str
    evidence_sources: List[EvidenceSourceOut] = []
    created_at: datetime.datetime

    class Config:
        from_attributes = True

# --- MEDICAL REPORT SCHEMAS ---
class MedicalReportBase(BaseModel):
    title: str
    report_type: str = "laboratory"

class MedicalReportCreate(MedicalReportBase):
    pass

class MedicalReportOut(MedicalReportBase):
    id: int
    user_id: int
    status: str
    original_filename: str
    file_size: Optional[int] = None
    summary: Optional[str] = None
    processing_error: Optional[str] = None
    created_at: datetime.datetime
    updated_at: datetime.datetime

    class Config:
        from_attributes = True

class MedicalReportDetailOut(MedicalReportOut):
    extracted_texts: List[ExtractedTextOut] = []
    medical_entities: List[MedicalEntityOut] = []
    analysis_results: List[AnalysisResultOut] = []

    class Config:
        from_attributes = True

# --- X-RAY ANALYSIS SCHEMAS ---
class XrayObservationItem(BaseModel):
    pathology: str
    score: float
    confidence_level: str  # Low, Moderate, High
    explanation: str
    literature_reference: Optional[str] = None

class XrayAnalysisOut(BaseModel):
    id: int
    user_id: int
    original_filename: str
    image_quality: str
    anatomical_region: str
    model_name: str
    model_version: str
    preliminary_findings: str
    observations_json: List[Dict[str, Any]]
    uncertainty_info: Optional[Dict[str, Any]] = None
    limitations_text: Optional[str] = None
    disclaimer: str
    created_at: datetime.datetime

    class Config:
        from_attributes = True

# --- DASHBOARD STATS SCHEMAS ---
class DashboardStatsOut(BaseModel):
    total_reports: int
    total_xrays: int
    completed_analyses: int
    pending_analyses: int
    recent_reports: List[MedicalReportOut] = []
    recent_xrays: List[XrayAnalysisOut] = []
    system_status: Dict[str, Any] = {}

