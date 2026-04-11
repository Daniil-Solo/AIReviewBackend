from abc import ABC, abstractmethod

from src.dto.emails.emails import EmailMessageDTO


class EmailSenderInterface(ABC):
    @abstractmethod
    async def send(self, message: EmailMessageDTO) -> None:
        raise NotImplementedError
