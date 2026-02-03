import requests

async def publish_event(event: dict):
    # temporary local simulation
    print(f"[BROKER] Publishing event: {event}")