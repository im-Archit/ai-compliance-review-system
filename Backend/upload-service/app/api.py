from fastapi import APIRouter, UploadFile, File, HTTPException
from app.events.gcp_pubsub import publish_event
from google.cloud import storage
import os
import uuid
from datetime import datetime
import requests

router = APIRouter(prefix="/api/v1/documents", tags=["documents"])

@router.post("/upload", status_code=202)
async def upload_document(file: UploadFile = File(...)):
    if file.content_type not in ["application/pdf", "image/png", "image/jpeg"]:
        raise HTTPException(status_code=400, detail="Unsupported file type")

    # ✅ document_id defined HERE
    document_id = str(uuid.uuid4())
    contents = await file.read()

    # Store file in Google Cloud Storage
    bucket_name = "ai-compliance-documents"
    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(f"{document_id}/{file.filename}")
    blob.upload_from_string(contents, content_type=file.content_type)
    storage_path = f"gs://{bucket_name}/{document_id}/{file.filename}"

    # -------------------------------------------------
    # Persist metadata to Compliance Store Service
    # -------------------------------------------------
    compliance_store_url = os.environ.get(
        "COMPLIANCE_STORE_URL",
        "http://127.0.0.1:8003"
    )

    try:
        requests.post(
            f"{compliance_store_url}/documents/metadata",
            json={
                "document_id": document_id,
                "filename": file.filename,
                "storage_path": storage_path,
                "content_type": file.content_type,
                "file_size": len(contents)
            },
            timeout=5
        )
    except Exception as e:
        print(f"[WARNING] Failed to persist metadata: {e}")

    # Publish standardized pipeline event
    publish_event({
        "event_type": "DOCUMENT_UPLOADED",
        "document_id": document_id,
        "timestamp": datetime.utcnow().isoformat(),
        "metadata": {
            "storage_path": storage_path,
            "content_type": file.content_type
        }
    })

    return {
        "document_id": document_id,
        "status": "UPLOADED",
        "storage_path": storage_path
    }
