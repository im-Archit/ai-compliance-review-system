from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional
from fastapi.middleware.cors import CORSMiddleware
from app import models
from fastapi import Query
from app.db import Base, engine, get_db
from app.consumer import start_consumer
from app.models import ComplianceDecision, AuditLog, User
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from app.models import DocumentMetadata
from google.cloud import storage
from urllib.parse import urlparse

app = FastAPI(title="Compliance Store Service")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =========================
# Security Configuration
# =========================

SECRET_KEY = "supersecretkey_change_in_production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = db.query(User).filter(User.username == username).first()
    if user is None or not user.enabled:
        raise credentials_exception

    return user


def require_role(allowed_roles: list[str]):
    def role_dependency(current_user: User = Depends(get_current_user)):
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=403,
                detail="You do not have permission to access this resource",
            )
        return current_user
    return role_dependency

def require_admin(current_user: User = Depends(get_current_user)):
    if current_user.role != "Admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user


def require_analyst_or_admin(current_user: User = Depends(get_current_user)):
    if current_user.role not in ["Admin", "Analyst"]:
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    return current_user



# =========================
# Response Models
# =========================

class DocumentMetadataRequest(BaseModel):
    document_id: str
    filename: str
    storage_path: str
    content_type: str
    file_size: float | None = None

class ComplianceDecisionResponse(BaseModel):
    document_id: str
    document_type: str
    risk_level: str
    status: str
    flags: list
    confidence: Optional[float] = None
    explanation: Optional[str] = None

    class Config:
        from_attributes = True

# =========================
# Document Metadata Model
# =========================


class DashboardMetricsResponse(BaseModel):
    totalDocuments: int
    highRiskCount: int
    lowRiskCount: int
    compliantCount: int
    nonCompliantCount: int
    avgConfidence: float


class SystemStatusResponse(BaseModel):
    service: str
    database: str
    totalDecisions: int
    totalAuditLogs: int
    lastDecisionAt: Optional[str] = None
    timestamp: str

class DecisionsListResponse(BaseModel):
    total: int
    limit: int
    offset: int
    data: list[ComplianceDecisionResponse]

# =========================
# Authentication Endpoints
# =========================


# =========================
# Authentication Models
# =========================

class LoginRequest(BaseModel):
    username: str
    password: str




@app.post("/auth/login")
def login(request: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == request.username).first()

    if not user or not verify_password(request.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid username or password")

    access_token = create_access_token(
        data={
            "sub": user.username,
            "role": user.role
        }
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "role": user.role
    }


# @app.post("/auth/login")
# def login(payload: LoginRequest, db: Session = Depends(get_db)):
#     user = db.query(User).filter(User.username == payload.username).first()

#     if not user or not verify_password(payload.password, user.hashed_password):
#         raise HTTPException(status_code=401, detail="Invalid username or password")

#     access_token = create_access_token(
#         data={
#             "sub": user.username,
#             "role": user.role
#         }
#     )

#     audit = AuditLog(
#         document_id="AUTH",
#         event="LOGIN",
#         details={"username": user.username}
#     )
#     db.add(audit)
#     db.commit()

#     return {
#         "access_token": access_token,
#         "token_type": "bearer",
#         "role": user.role
#     }


# =========================
# Decision Endpoints
# =========================

# =========================
# Document Metadata Endpoint (Internal)
# =========================

@app.post("/documents/metadata")
def create_document_metadata(
    payload: DocumentMetadataRequest,
    db: Session = Depends(get_db),
):
    existing = (
        db.query(DocumentMetadata)
        .filter(DocumentMetadata.document_id == payload.document_id)
        .first()
    )

    if existing:
        return {"status": "already_exists"}

    document = DocumentMetadata(
        document_id=payload.document_id,
        filename=payload.filename,
        storage_path=payload.storage_path,
        content_type=payload.content_type,
        file_size=payload.file_size,
    )

    db.add(document)
    db.commit()

    return {"status": "stored"}


# =========================
# Signed URL Endpoint
# =========================

@app.get("/documents/{document_id}/signed-url")
def get_signed_url(
    document_id: str,
    current_user: User = Depends(require_analyst_or_admin),
    db: Session = Depends(get_db),
):
    document = (
        db.query(DocumentMetadata)
        .filter(DocumentMetadata.document_id == document_id)
        .first()
    )

    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    # Parse gs://bucket/path
    parsed = document.storage_path.replace("gs://", "")
    bucket_name, blob_path = parsed.split("/", 1)

    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(blob_path)

    url = blob.generate_signed_url(
        version="v4",
        expiration=600,  # 10 minutes
        method="GET",
    )

    return {
        "signed_url": url,
        "filename": document.filename,
        "content_type": document.content_type,
    }


@app.get("/decisions", response_model=DecisionsListResponse)
def list_decisions(
    # current_user: User = Depends(get_current_user),            ############## I changed it 
    risk_level: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    document_id: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    query = db.query(ComplianceDecision)

    # 🔍 Apply filters if provided
    if risk_level:
        query = query.filter(ComplianceDecision.risk_level == risk_level)

    if status:
        query = query.filter(ComplianceDecision.status == status)

    if document_id:
        query = query.filter(ComplianceDecision.document_id.contains(document_id))

    total_count = query.count()

    results = (
        query.order_by(ComplianceDecision.created_at.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )

    # 📝 Audit log
    audit = AuditLog(
        document_id="*",
        event="DECISIONS_FILTERED",
        details={
            "risk_level": risk_level,
            "status": status,
            "document_id": document_id,
            "limit": limit,
            "offset": offset,
        },
    )
    db.add(audit)
    db.commit()

    return {
        "total": total_count,
        "limit": limit,
        "offset": offset,
        "data": results,
    }


@app.get("/compliance/{document_id}", response_model=ComplianceDecisionResponse)
def get_compliance_result(document_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),):
    decision = (
        db.query(ComplianceDecision)
        .filter(ComplianceDecision.document_id == document_id)
        .order_by(ComplianceDecision.created_at.desc())
        .first()
    )

    if not decision:
        raise HTTPException(status_code=404, detail="Compliance result not found")

    audit = AuditLog(
        document_id=document_id,
        event="COMPLIANCE_FETCHED",
        details={"endpoint": "get_compliance_result"},
    )
    db.add(audit)
    db.commit()

    return decision


# =========================
# Dashboard Metrics Endpoint
# =========================

@app.get("/dashboard-metrics", response_model=DashboardMetricsResponse)
def get_dashboard_metrics(current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),):
    
    total = db.query(func.count(ComplianceDecision.id)).scalar() or 0

    high_risk = (
        db.query(func.count(ComplianceDecision.id))
        .filter(ComplianceDecision.risk_level == "HIGH")
        .scalar()
        or 0
    )

    low_risk = (
        db.query(func.count(ComplianceDecision.id))
        .filter(ComplianceDecision.risk_level == "LOW")
        .scalar()
        or 0
    )

    compliant = (
        db.query(func.count(ComplianceDecision.id))
        .filter(ComplianceDecision.status == "COMPLIANT")
        .scalar()
        or 0
    )

    non_compliant = (
        db.query(func.count(ComplianceDecision.id))
        .filter(ComplianceDecision.status == "NON_COMPLIANT")
        .scalar()
        or 0
    )

    avg_confidence = (
        db.query(func.avg(ComplianceDecision.confidence)).scalar() or 0.0
    )

    return {
        "totalDocuments": total,
        "highRiskCount": high_risk,
        "lowRiskCount": low_risk,
        "compliantCount": compliant,
        "nonCompliantCount": non_compliant,
        "avgConfidence": round(float(avg_confidence), 2),
    }



# =========================
# Audit Logs Endpoint (Pagination + Filtering)
# =========================

@app.get("/audit-logs")
def list_audit_logs(
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    event: Optional[str] = Query(None),
    document_id: Optional[str] = Query(None),
):
    query = db.query(AuditLog)

    # 🔍 Apply filters if provided
    if event:
        query = query.filter(AuditLog.event == event)

    if document_id:
        query = query.filter(AuditLog.document_id == document_id)

    total_count = query.count()

    logs = (
        query.order_by(AuditLog.created_at.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )

    return {
        "total": total_count,
        "limit": limit,
        "offset": offset,
        "data": logs,
    }

# =========================
# System Monitoring Endpoint
# =========================

from sqlalchemy import text

@app.get("/system-status", response_model=SystemStatusResponse)
def get_system_status(current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),):
    from datetime import datetime

    # =========================
    # Database Health Check
    # =========================
    try:
        db.execute(text("SELECT 1"))
        database_status = "CONNECTED"
    except Exception:
        database_status = "DISCONNECTED"

    # =========================
    # Metrics
    # =========================
    total_decisions = db.query(func.count(ComplianceDecision.id)).scalar() or 0
    total_audit_logs = db.query(func.count(AuditLog.id)).scalar() or 0

    last_decision = (
        db.query(ComplianceDecision)
        .order_by(ComplianceDecision.created_at.desc())
        .first()
    )

    last_decision_time = (
        last_decision.created_at.isoformat()
        if last_decision and last_decision.created_at
        else None
    )

    return {
        "service": "UP",
        "database": database_status,
        "totalDecisions": total_decisions,
        "totalAuditLogs": total_audit_logs,
        "lastDecisionAt": last_decision_time,
        "timestamp": datetime.utcnow().isoformat(),
    }


# =========================
# Health
# =========================

@app.get("/health")
def health():
    return {"status": "ok"}


# =========================
# Startup
# =========================

# @app.on_event("startup")
# def startup():
#     from app.models import User
#     from sqlalchemy.orm import Session

#     db = next(get_db())
#     admin_exists = db.query(User).filter(User.username == "admin").first()
#     if not admin_exists:
#         admin_user = User(
#             username="admin",
#             hashed_password=get_password_hash("admin"),
#             role="Admin",
#             enabled=True,
#         )
#         db.add(admin_user)
#         db.commit()
#     Base.metadata.create_all(bind=engine)
#     start_consumer()

@app.on_event("startup")
def startup():
    # 1️⃣ Ensure all tables exist FIRST
    Base.metadata.create_all(bind=engine)

    # 2️⃣ Open DB session
    db = next(get_db())

    # 3️⃣ Check if admin exists
    admin_exists = db.query(User).filter(User.username == "admin").first()

    # 4️⃣ Create admin if missing
    if not admin_exists:
        admin_user = User(
            username="admin",
            hashed_password=get_password_hash("admin"),
            role="Admin",
            enabled=True,
        )
        db.add(admin_user)
        db.commit()
    # Create Analyst user if not exists
    analyst_exists = db.query(User).filter(User.username == "analyst").first()
    if not analyst_exists:
        analyst_user = User(
            username="analyst",
            hashed_password=get_password_hash("analyst"),
            role="Analyst",
            enabled=True,
        )
        db.add(analyst_user)
        db.commit()

# Create Reviewer user if not exists
    reviewer_exists = db.query(User).filter(User.username == "reviewer").first()
    if not reviewer_exists:
        reviewer_user = User(
            username="reviewer",
            hashed_password=get_password_hash("reviewer"),
            role="Reviewer",
            enabled=True,
        )
        db.add(reviewer_user)
        db.commit()
    # 5️⃣ Start consumer
    start_consumer()