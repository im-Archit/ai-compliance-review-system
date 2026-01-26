import os
from app.storage.base import StorageClient

class LocalStorageClient(StorageClient):

    def __init__(self, base_path: str = "data"):
        self.base_path = base_path
        os.makedirs(self.base_path, exist_ok=True)

    async def save(self, document_id: str, file_bytes: bytes) -> str:
        file_path = os.path.join(self.base_path, f"{document_id}")
        with open(file_path, "wb") as f:
            f.write(file_bytes)
        return file_path