from abc import ABC, abstractmethod


class IStorageService(ABC):
    @abstractmethod
    async def upload_file(
        self, file_bytes: bytes, filename: str, content_type: str, bucket: str = "attachments"
    ) -> str:
        """Uploads file and returns public or accessible URL."""
        pass

    @abstractmethod
    async def delete_file(self, file_url: str) -> bool:
        pass
