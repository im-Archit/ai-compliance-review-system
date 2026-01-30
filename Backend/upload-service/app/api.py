from fastapi import APIRouter, UploadFile, File, HTTPException
from app.storage.local import LocalStorageClient
from app.events.local import LocalEventPublisher
from app.db import SessionLocal, Document
import uuid
from datetime import datetime

from app.storage.local import LocalStorageClient
from app.db import SessionLocal, Document
from app.events.gcp_pubsub import publish_event

router = APIRouter(prefix="/api/v1/documents", tags=["documents"])

@router.post("/upload", status_code=202)
async def upload_document(file: UploadFile = File(...)):
    if file.content_type not in ["application/pdf", "image/png", "image/jpeg"]:
        raise HTTPException(status_code=400, detail="Unsupported file type")

    # ✅ document_id defined HERE
    document_id = str(uuid.uuid4())
    contents = await file.read()

    # Store file
    storage = LocalStorageClient()
    storage_path = await storage.save(document_id, contents)

    # Save metadata
    db = SessionLocal()
    doc = Document(
        id=document_id,
        status="UPLOADED",
        storage_path=storage_path
    )
    db.add(doc)
    db.commit()
    db.close()

    # Publish Pub/Sub event
    publish_event({
        "document_id": document_id,
        "storage_path": storage_path,
        "uploaded_at": datetime.utcnow().isoformat()
    })

    return {
        "document_id": document_id,
        "status": "UPLOADED",
        "storage_path": storage_path
    }

db = SessionLocal()
doc = Document(
    id=document_id,
    status="UPLOADED",
    storage_path=storage_path
)
db.add(doc)
db.commit()
db.close()

async def publish_event():
    publisher = LocalEventPublisher()
    await publisher.publish(
        "DocumentUploaded",
        {
            "document_id": document_id,
            "storage_path": storage_path
        }
    )

import asyncio
asyncio.run(publish_event())
