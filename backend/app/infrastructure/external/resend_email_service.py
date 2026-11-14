import logging
from typing import List, Optional
from app.application.interfaces.services.i_email_service import IEmailService
from app.config import settings

logger = logging.getLogger(__name__)


class ResendEmailService(IEmailService):
    def __init__(
        self,
        api_key: Optional[str] = settings.resend_api_key,
        from_email: str = settings.email_from,
    ):
        self.api_key = api_key
        self.from_email = from_email
        self.resend = None

        if self.api_key:
            try:
                import resend
                resend.api_key = self.api_key
                self.resend = resend
            except Exception:
                self.resend = None

    async def send_email(self, to: str, subject: str, html_content: str) -> bool:
        if self.resend:
            try:
                params = {
                    "from": self.from_email,
                    "to": [to],
                    "subject": subject,
                    "html": html_content,
                }
                self.resend.Emails.send(params)
                return True
            except Exception as e:
                logger.warning(f"Failed to send email via Resend to {to}: {e}")
                return False

        logger.info(f"[MockEmail] To: {to} | Subject: {subject}")
        return True

    async def send_bulk_email(self, to_list: List[str], subject: str, html_content: str) -> bool:
        if not to_list:
            return True

        if self.resend:
            try:
                for recipient in to_list:
                    params = {
                        "from": self.from_email,
                        "to": [recipient],
                        "subject": subject,
                        "html": html_content,
                    }
                    self.resend.Emails.send(params)
                return True
            except Exception as e:
                logger.warning(f"Failed to send bulk email via Resend: {e}")
                return False

        logger.info(f"[MockBulkEmail] To: {len(to_list)} recipients | Subject: {subject}")
        return True
