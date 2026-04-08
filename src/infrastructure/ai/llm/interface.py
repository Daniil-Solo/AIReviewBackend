from abc import ABC, abstractmethod
from typing import Any, Literal

from src.dto.ai_review.message import InputMessageDTO, AIAnswerDTO


class LLMInterface(ABC):
    @abstractmethod
    def answer(self, messages: list[InputMessageDTO], **kwargs: Any) -> AIAnswerDTO:
        pass
