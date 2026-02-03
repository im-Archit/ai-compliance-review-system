# Pipeline steps logic
async def process_document(event):
    document_id = event["document_id"]

    print(f"OCR step for {document_id}")
    # ... OCR logic

    print(f"Classification step for {document_id}")
    document_type = "education_certificate"

    print(f"Risk analysis step for {document_id}")
    risk_level = "LOW"

    result = {
        "document_type": document_type,
        "risk_level": risk_level,
        "flags": [],
        "confidence": 0.95
    }

    print(f"Pipeline completed for document {document_id}")

    return result

async def run_ocr(document_id: str):
    print(f"OCR step for {document_id}")

async def classify_document(document_id: str):
    print(f"Classification step for {document_id}")

async def analyze_risk(document_id: str):
    print(f"Risk analysis step for {document_id}")