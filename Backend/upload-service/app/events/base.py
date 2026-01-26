from abc import ABC, abstractmethod

class EventPublisher(ABC):

    @abstractmethod
    async def publish(self, event_name: str, payload: dict):
        pass