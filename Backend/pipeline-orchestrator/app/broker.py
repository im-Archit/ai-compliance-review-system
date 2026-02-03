import asyncio

EVENT_QUEUE = asyncio.Queue()

async def publish_event(event: dict):
    await EVENT_QUEUE.put(event)

async def consume_event():
    return await EVENT_QUEUE.get()