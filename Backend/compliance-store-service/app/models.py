import uuid
from sqlalchemy import Column, String, Float, DateTime, JSON
from datetime import datetime
from app.db import Base
from sqlalchemy import Text
from sqlalchemy import Boolean
from sqlalchemy import Enum
import enum

class ProcessingStage(str, enum.Enum):
    RECEIVED = "RECEIVED"
    OCR_COMPLETED = "OCR_COMPLETED"
    ANALYZED = "ANALYZED"
    STORED = "STORED"
    REVIEW_PENDING = "REVIEW_PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"


class ReviewStatus(str, enum.Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"


class ComplianceDecision(Base):
    __tablename__ = "compliance_decisions"

    id = Column(
        String,
        primary_key=True,
        index=True,
        default=lambda: str(uuid.uuid4()),
        nullable=False,
    )

    document_id = Column(String, unique=True, index=True, nullable=False)
    document_type = Column(String, nullable=False)
    risk_level = Column(String, nullable=False)

    # Store rule hits / explainability
    flags = Column(JSON, nullable=False, default=list)

    # Confidence score from rules engine
    confidence = Column(Float, nullable=False, default=1.0)

    ai_summary = Column(String, nullable=True)

    # When the document was evaluated by the pipeline
    evaluated_at = Column(DateTime, nullable=True, default=datetime.utcnow)

    status = Column(String, nullable=False)

    # Processing lifecycle stage
    processing_stage = Column(
        Enum(ProcessingStage),
        default=ProcessingStage.RECEIVED,
        nullable=False,
    )

    # Reviewer workflow status
    review_status = Column(
        Enum(ReviewStatus),
        default=ReviewStatus.PENDING,
        nullable=False,
    )

    explanation = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

 # =========================
 # Document Metadata (Storage Layer)
 # =========================

class DocumentMetadata(Base):
    __tablename__ = "documents"

    id = Column(
        String,
        primary_key=True,
        index=True,
        default=lambda: str(uuid.uuid4()),
        nullable=False,
    )

    # Same document_id used across pipeline
    document_id = Column(String, unique=True, index=True, nullable=False)

    filename = Column(String, nullable=False)

    # Full GCS path: gs://bucket/path/file.pdf
    storage_path = Column(String, nullable=False)

    content_type = Column(String, nullable=False)

    file_size = Column(Float, nullable=True)

    uploaded_at = Column(DateTime, default=datetime.utcnow)

    # Optional: track who uploaded it (future enhancement)
    uploaded_by = Column(String, nullable=True)


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(
        String,
        primary_key=True,
        index=True,
        default=lambda: str(uuid.uuid4()),
        nullable=False,
    )

    document_id = Column(String, index=True, nullable=False)

    event = Column(String, nullable=False)

    details = Column(JSON, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)

# =========================
# User & Role Management
# =========================

class UserRole(str, enum.Enum):
    ADMIN = "Admin"
    ANALYST = "Analyst"
    REVIEWER = "Reviewer"



class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    username = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(String, nullable=False)
    enabled = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    last_login = Column(DateTime, nullable=True)