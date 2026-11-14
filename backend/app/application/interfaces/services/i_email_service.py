from abc import ABC, abstractmethod
from typing import List, Optional


class IEmailService(ABC):
    @abstractmethod
    async def send_email(
        self, to: str, subject: str, html_content: str
    ) -> bool:
        pass

    @abstractmethod
    async def send_bulk_email(
        self, to_list: List[str], subject: str, html_content: str
    ) -> bool:
        pass
