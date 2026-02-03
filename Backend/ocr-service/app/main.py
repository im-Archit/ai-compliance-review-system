from fastapi import FastAPI
from app.consumer import start_consumer
import threading

app = FastAPI(title="OCR Service")

@app.on_event("startup")
def startup():
    thread = threading.Thread(
        target=start_consumer,
        daemon=True
    )
    thread.start()

@app.get("/health")
def health():
    return {"status": "ocr-running"}