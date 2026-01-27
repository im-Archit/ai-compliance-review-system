# Pipeline steps logic
async def process_document(event: dict):
    document_id = event["document_id"]

    print(f"Starting pipeline for document {document_id}")

    await run_ocr(document_id)
    await classify_document(document_id)
    await analyze_risk(document_id)

    print(f"Pipeline completed for document {document_id}")

async def run_ocr(document_id: str):
    print(f"OCR step for {document_id}")

async def classify_document(document_id: str):
    print(f"Classification step for {document_id}")

async def analyze_risk(document_id: str):
    print(f"Risk analysis step for {document_id}")