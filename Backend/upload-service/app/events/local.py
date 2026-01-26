import json

class LocalEventPublisher:

    async def publish(self, event_name: str, payload: dict):
        print(f"[EVENT] {event_name}: {json.dumps(payload)}")