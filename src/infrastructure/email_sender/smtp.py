import aiosmtplib
from email.message import EmailMessage

from src.dto.emails.emails import EmailMessageDTO
from src.infrastructure.email_sender.interface import EmailSenderInterface
from src.infrastructure.logging import get_logger


logger = get_logger()


class SmtpEmailSender(EmailSenderInterface):
    def __init__(
        self,
        host: str,
        port: int,
        user: str,
        password: str,
        use_tls: bool = True,
    ) -> None:
        self._host = host
        self._port = port
        self._user = user
        self._password = password
        self._use_tls = use_tls

    async def send(self, message: EmailMessageDTO) -> None:
        email_msg = EmailMessage()
        email_msg["From"] = f"{message.from_display_name} <{message.from_email}>"
        email_msg["To"] = ", ".join(message.to)
        email_msg["Cc"] = ", ".join(message.cc)
        email_msg["Bcc"] = ", ".join(message.bcc)
        email_msg["Subject"] = message.subject
        email_msg.set_content(message.plain)
        email_msg.add_alternative(message.html, subtype="html")

        try:
            await aiosmtplib.send(
                email_msg,
                hostname=self._host,
                port=self._port,
                username=self._user,
                password=self._password,
                use_tls=self._use_tls,
            )
        except Exception:
            logger.exception("Failed to send email", to=message.to, subject=message.subject)
            raise
