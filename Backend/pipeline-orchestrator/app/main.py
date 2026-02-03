# Service entry point
from fastapi import FastAPI
from app.consumer import start_consumer
import threading

app = FastAPI(title="Pipeline Orchestrator")

@app.on_event("startup")
def startup_event():
    thread = threading.Thread(target=start_consumer, daemon=True)
    thread.start()

@app.get("/health")
def health():
    return {"status": "ok"}