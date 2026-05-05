from src.dto.emails.emails import EmailMessageDTO
from src.infrastructure.email_sender.interface import EmailSenderInterface
from src.infrastructure.logging import get_logger


logger = get_logger()


class DisabledEmailSender(EmailSenderInterface):
    async def send(self, message: EmailMessageDTO) -> None:
        logger.warning(
            "Email sending is disabled, skipping email",
            to=message.to,
            subject=message.subject,
        )
