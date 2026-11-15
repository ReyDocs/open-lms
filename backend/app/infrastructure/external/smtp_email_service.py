import logging
from email.message import EmailMessage
from typing import List, Optional
import aiosmtplib

from app.application.interfaces.services.i_email_service import IEmailService
from app.config import settings

logger = logging.getLogger(__name__)


class SmtpEmailService(IEmailService):
    """
    Direct asynchronous SMTP email service implementation using aiosmtplib.
    Works with standard SMTP providers (Gmail, Outlook, Mailgun, SendGrid, Mailpit, Postfix, etc.).
    """

    def __init__(
        self,
        hostname: Optional[str] = settings.smtp_host,
        port: int = settings.smtp_port,
        username: Optional[str] = settings.smtp_user,
        password: Optional[str] = settings.smtp_password,
        use_tls: bool = settings.smtp_use_tls,
        start_tls: bool = settings.smtp_starttls,
        from_email: str = settings.email_from,
    ):
        self.hostname = hostname
        self.port = port
        self.username = username
        self.password = password
        self.use_tls = use_tls
        self.start_tls = start_tls
        self.from_email = from_email

    async def send_email(self, to: str, subject: str, html_content: str) -> bool:
        if not self.hostname:
            logger.info(f"[MockEmail] (SMTP unconfigured) To: {to} | Subject: {subject}")
            return True

        message = EmailMessage()
        message["From"] = self.from_email
        message["To"] = to
        message["Subject"] = subject
        message.set_content(html_content, subtype="html")

        try:
            await aiosmtplib.send(
                message,
                hostname=self.hostname,
                port=self.port,
                username=self.username if self.username else None,
                password=self.password if self.password else None,
                use_tls=self.use_tls,
                start_tls=self.start_tls,
            )
            logger.info(f"Email sent successfully via SMTP to {to}")
            return True
        except Exception as e:
            logger.warning(f"Failed to send email via SMTP to {to}: {e}")
            return False

    async def send_bulk_email(self, to_list: List[str], subject: str, html_content: str) -> bool:
        if not to_list:
            return True

        if not self.hostname:
            logger.info(f"[MockBulkEmail] (SMTP unconfigured) To: {len(to_list)} recipients | Subject: {subject}")
            return True

        success = True
        for recipient in to_list:
            ok = await self.send_email(recipient, subject, html_content)
            if not ok:
                success = False

        return success
