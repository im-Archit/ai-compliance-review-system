from fastapi import APIRouter, UploadFile, File, HTTPException
from app.storage.local import LocalStorageClient
from app.events.local import LocalEventPublisher
from app.db import SessionLocal, Document
import uuid

router = APIRouter(prefix="/api/v1/documents", tags=["documents"])

@router.post("/upload", status_code=202)
async def upload_document(file: UploadFile = File(...)):
    if file.content_type not in ["application/pdf", "image/png", "image/jpeg"]:
        raise HTTPException(status_code=400, detail="Unsupported file type")

    document_id = str(uuid.uuid4())
    contents = await file.read()

    storage = LocalStorageClient()
    storage_path = await storage.save(document_id, contents)

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
