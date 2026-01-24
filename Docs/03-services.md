# Service Decomposition

This project is structured as multiple independently deployable services, simulating a real enterprise microservices environment.

Each service has a clearly defined responsibility and ownership boundary.

---

## Services Overview

### 1. Upload Service
**Responsibility**
- User authentication
- File validation
- Upload orchestration

**Tech**
- FastAPI
- JWT-based authentication
- Cloud Storage SDK

---

### 2. Storage Layer
**Responsibility**
- Durable storage of raw documents
- Versioning and metadata tagging

**Tech**
- Google Cloud Storage

---

### 3. Event Broker
**Responsibility**
- Publish document ingestion events
- Decouple upload from processing

**Tech**
- GCP Pub/Sub

---

### 4. OCR Service
**Responsibility**
- Extract raw text from documents (PDF, images)
- Normalize extracted content

**Tech**
- GCP Vision API
- Python

---

### 5. Classification Service
**Responsibility**
- Identify document type
- Assign intent labels
- Generate confidence scores

**Tech**
- Transformer-based text classification
- Python (FastAPI)

---

### 6. Risk Analysis Engine
**Responsibility**
- Apply compliance rules
- Identify missing or risky clauses
- Generate explainable flags

**Tech**
- Rule-based logic
- ML-assisted scoring

---

### 7. Results API
**Responsibility**
- Persist processing results
- Expose data to dashboard

**Tech**
- FastAPI
- PostgreSQL

---

### 8. Dashboard
**Responsibility**
- Visualize document status
- Display AI outputs and recommendations

**Tech**
- Next.js
- Server Components