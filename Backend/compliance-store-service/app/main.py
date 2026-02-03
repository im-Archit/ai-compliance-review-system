from fastapi import FastAPI
from app.db import Base, engine
from app.consumer import start_consumer
from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.db import get_db
from app.models import ComplianceDecision

app = FastAPI(title="Compliance Store Service")

@app.get("/decisions/{document_id}")
def get_decision(document_id: str, db: Session = Depends(get_db)):
    decision = db.query(ComplianceDecision).filter(
        ComplianceDecision.document_id == document_id
    ).first()

    if not decision:
        raise HTTPException(status_code=404, detail="Decision not found")

    return decision


@app.get("/decisions")
def list_decisions(
    risk_level: str | None = None,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    query = db.query(ComplianceDecision)

    if risk_level:
        query = query.filter(ComplianceDecision.risk_level == risk_level)

    return query.limit(limit).all()

@app.on_event("startup")
def startup():
    Base.metadata.create_all(bind=engine)
    start_consumer()

@app.get("/health")
def health():
    return {"status": "ok"}