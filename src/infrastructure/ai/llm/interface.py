from abc import ABC, abstractmethod
from typing import Any

from src.dto.ai_review.message import AIAnswerDTO, InputMessageDTO


class LLMInterface(ABC):
    @abstractmethod
    def answer(self, messages: list[InputMessageDTO], **kwargs: Any) -> AIAnswerDTO:
        pass
