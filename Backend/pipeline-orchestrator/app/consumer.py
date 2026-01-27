# Event subscription
import asyncio
from app.pipeline import process_document

async def start_consumer():
    # Simulated event listener
    asyncio.create_task(mock_event_listener())

async def mock_event_listener():
    while True:
        await asyncio.sleep(10)
        event = {
            "document_id": "sample-id",
            "storage_path": "data/sample"
        }
        await process_document(event)