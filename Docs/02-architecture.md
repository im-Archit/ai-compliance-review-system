# System Architecture

## Architectural Overview

The AI-Assisted Compliance Review System is designed as an **event-driven, cloud-native pipeline**.  
Each processing stage is implemented as an independent service, enabling scalability, fault isolation, and future extensibility.

The architecture mirrors real-world enterprise document processing systems used in GovTech, FinTech, and RegTech environments.

---

## High-Level Architecture

1. Users upload documents via a secure web interface.
2. Documents are stored in cloud object storage.
3. A storage event triggers an asynchronous processing pipeline.
4. Multiple AI services process the document in sequence.
5. Results are persisted and exposed through APIs and dashboards.

---

## Component Diagram (Logical)
[ Web App (Next.js) ]
|
v
[ Upload API Service ]
|
v
[ Cloud Storage (GCS) ]
|
v
[ Pub/Sub Event: DocumentUploaded ]
|
v
[ Pipeline Orchestrator ]
|        |        |
v        v        v
[ OCR ]  [ Classifier ]  [ Risk Engine ]
\        |        /
[ Results Store ]
|
v
[ Dashboard + APIs ]

---

## Design Principles

- **Event-driven**: No tight coupling between services
- **Stateless services**: Enables horizontal scaling
- **Asynchronous processing**: Improves throughput and resilience
- **Explainability-first AI**: Outputs include confidence and reasoning
- **Cloud-native**: Designed for managed services and serverless execution

---

## Technology Summary

| Layer | Technology |
|-----|-----------|
| Frontend | Next.js (App Router) |
| Backend APIs | FastAPI |
| Messaging | GCP Pub/Sub |
| Storage | GCP Cloud Storage |
| Database | PostgreSQL |
| AI / ML | Python, Transformer-based models |
| Deployment | Docker, Cloud Run |
| CI/CD | GitHub Actions |