import uuid
from sqlalchemy import Column, String, Float, DateTime, JSON
from datetime import datetime
from app.db import Base

class ComplianceDecision(Base):
    __tablename__ = "compliance_decisions"

    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    document_id = Column(String, index=True)
    document_type = Column(String)
    risk_level = Column(String)
    flags = Column(JSON)
    confidence = Column(Float)
    evaluated_at = Column(DateTime)
    status = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)