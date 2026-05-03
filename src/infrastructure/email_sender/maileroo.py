from httpx import AsyncClient

from src.dto.emails.emails import EmailMessageDTO
from src.infrastructure.email_sender.interface import EmailSenderInterface
from src.infrastructure.logging import get_logger


logger = get_logger()


class MailerooEmailSender(EmailSenderInterface):
    def __init__(self, token: str, from_email: str, from_email_name: str) -> None:
        self._client = AsyncClient(
            base_url="https://smtp.maileroo.com",
            headers={"Authorization": f"Bearer {token}"},
        )
        self._from_email = from_email
        self._from_email_name = from_email_name

    async def send(self, message: EmailMessageDTO) -> None:
        data = {
            "from": {"address": self._from_email, "display_name": self._from_email_name},
            "to": [{"address": email} for email in message.to],
            "subject": message.subject,
            "html": message.html,
            "plain": message.plain,
            "tracking": True,
        }
        try:
            async with self._client as client:
                response = await client.post(
                    url="/api/v2/emails",
                    json=data,
                )
            response.raise_for_status()
        except Exception:
            logger.exception("Failed to send email", to=message.to, subject=message.subject)
            raise
