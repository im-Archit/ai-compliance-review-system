# Service entry point
from dotenv import load_dotenv
import os
from fastapi import FastAPI
from app.consumer import start_consumer
import threading

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(BASE_DIR, ".env"))

app = FastAPI(title="Pipeline Orchestrator")

@app.on_event("startup")
def startup_event():
    thread = threading.Thread(target=start_consumer, daemon=True)
    thread.start()

@app.get("/health")
def health():
    return {"status": "ok"}