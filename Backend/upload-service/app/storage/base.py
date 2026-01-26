from abc import ABC, abstractmethod

class StorageClient(ABC):

    @abstractmethod
    async def save(self, document_id: str, file_bytes: bytes) -> str:
        pass