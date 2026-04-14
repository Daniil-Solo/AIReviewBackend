from abc import ABC, abstractmethod
from typing import Any

from src.dto.ai_review.message import AIAnswerDTO, InputMessageDTO


class LLMInterface(ABC):
    @abstractmethod
    async def answer(self, messages: list[InputMessageDTO], **kwargs: Any) -> AIAnswerDTO:
        pass

    @abstractmethod
    async def run(self, system_text: str, user_text: str, **kwargs: Any) -> AIAnswerDTO:
        pass