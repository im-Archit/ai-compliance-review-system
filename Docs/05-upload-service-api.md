# Upload Service API Specification

## Purpose

The Upload Service is responsible for securely accepting documents from users,
validating them, storing them in cloud storage, and emitting an event to trigger
downstream processing pipelines.

This service does NOT perform any AI processing.

---

## API Endpoints

### POST /api/v1/documents/upload

Uploads a document for compliance analysis.

#### Request
- Authentication: JWT (mocked in Phase 1)
- Content-Type: multipart/form-data

**Fields**
- file: PDF or image document
- document_type (optional): user-provided hint

#### Validation Rules
- Max file size: 10 MB
- Allowed types: PDF, PNG, JPG
- Reject empty or corrupted files

---

#### Response (202 Accepted)

```json
{
  "document_id": "uuid",
  "status": "UPLOADED",
  "message": "Document accepted for processing"
}