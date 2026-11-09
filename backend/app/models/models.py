import datetime
from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    DateTime,
    ForeignKey,
    Text,
    Float,
    JSON,
    Index,
)
from sqlalchemy.orm import relationship
from backend.app.database.session import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    created_at = Column(
        DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc)
    )
    updated_at = Column(
        DateTime,
        default=lambda: datetime.datetime.now(datetime.timezone.utc),
        onupdate=lambda: datetime.datetime.now(datetime.timezone.utc),
    )

    # Relationships
    reports = relationship(
        "MedicalReport", back_populates="user", cascade="all, delete-orphan"
    )
    xray_analyses = relationship(
        "XrayAnalysis", back_populates="user", cascade="all, delete-orphan"
    )
    activity_logs = relationship(
        "ActivityLog", back_populates="user", cascade="all, delete-orphan"
    )


class MedicalReport(Base):
    __tablename__ = "medical_reports"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    title = Column(String(255), nullable=False)
    report_type = Column(
        String(50), default="laboratory"
    )  # laboratory, radiology, discharge, prescription
    status = Column(
        String(50), default="pending"
    )  # pending, processing, completed, failed
    file_path = Column(String(512), nullable=True)
    original_filename = Column(String(255), nullable=False)
    file_size = Column(Integer, nullable=True)
    summary = Column(Text, nullable=True)
    processing_error = Column(Text, nullable=True)
    created_at = Column(
        DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc)
    )
    updated_at = Column(
        DateTime,
        default=lambda: datetime.datetime.now(datetime.timezone.utc),
        onupdate=lambda: datetime.datetime.now(datetime.timezone.utc),
    )

    # Relationships
    user = relationship("User", back_populates="reports")
    uploaded_files = relationship(
        "UploadedFile", back_populates="report", cascade="all, delete-orphan"
    )
    extracted_texts = relationship(
        "ExtractedText", back_populates="report", cascade="all, delete-orphan"
    )
    medical_entities = relationship(
        "MedicalEntity", back_populates="report", cascade="all, delete-orphan"
    )
    analysis_results = relationship(
        "AnalysisResult", back_populates="report", cascade="all, delete-orphan"
    )


class UploadedFile(Base):
    __tablename__ = "uploaded_files"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    report_id = Column(
        Integer,
        ForeignKey("medical_reports.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    filename = Column(String(255), nullable=False)
    file_path = Column(String(512), nullable=False)
    file_size = Column(Integer, nullable=False)
    mime_type = Column(String(100), nullable=False)
    file_hash = Column(String(64), nullable=True)
    uploaded_at = Column(
        DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc)
    )

    report = relationship("MedicalReport", back_populates="uploaded_files")


class ExtractedText(Base):
    __tablename__ = "extracted_text"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    report_id = Column(
        Integer,
        ForeignKey("medical_reports.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    page_number = Column(Integer, default=1)
    raw_text = Column(Text, nullable=False)
    ocr_engine = Column(
        String(50), default="cloud-ocr"
    )  # cloud_ocr, pypdf
    confidence_score = Column(Float, nullable=True)
    bounding_boxes = Column(JSON, nullable=True)
    created_at = Column(
        DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc)
    )

    report = relationship("MedicalReport", back_populates="extracted_texts")


class MedicalEntity(Base):
    __tablename__ = "medical_entities"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    report_id = Column(
        Integer,
        ForeignKey("medical_reports.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    entity_type = Column(
        String(50), nullable=False
    )  # lab_test, disease, symptom, medication, anatomy, date
    text = Column(String(255), nullable=False)
    normalized_value = Column(String(100), nullable=True)
    unit = Column(String(50), nullable=True)
    reference_range = Column(String(100), nullable=True)
    is_out_of_range = Column(Boolean, nullable=True)
    flag = Column(String(20), nullable=True)  # LOW, NORMAL, HIGH, CRITICAL
    source_page = Column(Integer, default=1)
    confidence_score = Column(Float, nullable=True)
    created_at = Column(
        DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc)
    )

    report = relationship("MedicalReport", back_populates="medical_entities")


class AnalysisResult(Base):
    __tablename__ = "analysis_results"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    report_id = Column(
        Integer,
        ForeignKey("medical_reports.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    summary_text = Column(Text, nullable=False)
    patient_friendly_explanation = Column(Text, nullable=False)
    terminology_explanations = Column(JSON, nullable=True)
    doctor_discussion_questions = Column(JSON, nullable=True)
    uncertainty_score = Column(Float, default=0.0)
    ocr_confidence = Column(Float, nullable=True)
    extraction_confidence = Column(Float, nullable=True)
    model_used = Column(String(100), default="qwen2.5:latest")
    created_at = Column(
        DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc)
    )

    report = relationship("MedicalReport", back_populates="analysis_results")
    evidence_sources = relationship(
        "EvidenceSource", back_populates="analysis", cascade="all, delete-orphan"
    )


class XrayAnalysis(Base):
    __tablename__ = "xray_analyses"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    original_filename = Column(String(255), nullable=False)
    file_path = Column(String(512), nullable=False)
    image_quality = Column(String(50), default="acceptable")
    anatomical_region = Column(String(100), default="Chest (PA/AP)")
    model_name = Column(String(100), default="Hosted-Medical-Imaging-API")
    model_version = Column(String(50), default="cloud-v1")
    preliminary_findings = Column(Text, nullable=False)
    observations_json = Column(JSON, nullable=False)
    uncertainty_info = Column(JSON, nullable=True)
    limitations_text = Column(Text, nullable=True)
    disclaimer = Column(Text, nullable=False)
    created_at = Column(
        DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc)
    )

    user = relationship("User", back_populates="xray_analyses")


class KnowledgeDocument(Base):
    __tablename__ = "knowledge_documents"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    document_id = Column(String(100), unique=True, index=True, nullable=False)
    topic = Column(String(100), nullable=False)
    subtopic = Column(String(100), nullable=False)
    source_org = Column(String(255), nullable=False)
    title = Column(String(255), nullable=False)
    source_url = Column(String(512), nullable=False)
    category = Column(String(50), nullable=False)
    content = Column(Text, nullable=False)
    clinical_significance = Column(Text, nullable=True)
    created_at = Column(
        DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc)
    )

    embeddings = relationship(
        "DocumentEmbedding", back_populates="document", cascade="all, delete-orphan"
    )


class DocumentEmbedding(Base):
    __tablename__ = "document_embeddings"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    knowledge_doc_id = Column(
        Integer,
        ForeignKey("knowledge_documents.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    chunk_index = Column(Integer, default=0)
    chunk_text = Column(Text, nullable=False)
    embedding_model = Column(
        String(100), default="cloud-biomedical-embedder-v1"
    )
    vector_id = Column(String(100), nullable=True)
    created_at = Column(
        DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc)
    )

    document = relationship("KnowledgeDocument", back_populates="embeddings")


class EvidenceSource(Base):
    __tablename__ = "evidence_sources"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    analysis_id = Column(
        Integer,
        ForeignKey("analysis_results.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    knowledge_doc_id = Column(Integer, nullable=True)
    relevance_score = Column(Float, default=0.0)
    excerpt = Column(Text, nullable=False)
    source_org = Column(String(255), nullable=False)
    source_title = Column(String(255), nullable=False)
    source_url = Column(String(512), nullable=False)
    retrieved_at = Column(
        DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc)
    )

    analysis = relationship("AnalysisResult", back_populates="evidence_sources")


class ActivityLog(Base):
    __tablename__ = "activity_logs"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    action = Column(String(100), nullable=False)
    resource_type = Column(String(50), nullable=True)
    resource_id = Column(String(50), nullable=True)
    details = Column(JSON, nullable=True)
    ip_address = Column(String(45), nullable=True)
    created_at = Column(
        DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc)
    )

    user = relationship("User", back_populates="activity_logs")


# Module exports
__all__ = [
    "User",
    "MedicalReport",
    "UploadedFile",
    "ExtractedText",
    "MedicalEntity",
    "AnalysisResult",
    "XrayAnalysis",
    "KnowledgeDocument",
    "DocumentEmbedding",
    "EvidenceSource",
    "ActivityLog",
]

