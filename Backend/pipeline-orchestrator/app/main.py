# Service entry point
from fastapi import FastAPI
from app.consumer import start_consumer

app = FastAPI(title="Pipeline Orchestrator")

@app.on_event("startup")
async def startup_event():
    await start_consumer()

@app.get("/health")
async def health_check():
    return {"status": "ok"}