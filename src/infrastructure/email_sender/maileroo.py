from httpx import AsyncClient

from src.dto.emails.emails import EmailMessageDTO
from src.infrastructure.email_sender.interface import EmailSenderInterface
from src.infrastructure.logging import get_logger


logger = get_logger()


class MailerooEmailSender(EmailSenderInterface):
    def __init__(self, token: str) -> None:
        self._client = AsyncClient(
            base_url="https://smtp.maileroo.com",
            headers={"Authorization": f"Bearer {token}"},
        )

    async def send(self, message: EmailMessageDTO) -> None:
        data = {
            "from": {"address": message.from_email, "display_name": message.from_display_name},
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
