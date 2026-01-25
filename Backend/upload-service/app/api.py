from fastapi import APIRouter, UploadFile, File, HTTPException
import uuid

router = APIRouter(prefix="/api/v1/documents", tags=["documents"])

@router.post("/upload", status_code=202)
async def upload_document(file: UploadFile = File(...)):
    if file.content_type not in ["application/pdf", "image/png", "image/jpeg"]:
        raise HTTPException(status_code=400, detail="Unsupported file type")

    document_id = str(uuid.uuid4())

    return {
        "document_id": document_id,
        "status": "UPLOADED",
        "message": "Document accepted for processing"
    }