from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Literal


@dataclass
class Answer:
    content: str | None = None
    in_tokens: int | None = None
    out_tokens: int | None = None


@dataclass
class Message:
    role: Literal["system", "user", "assistant"]
    content: str


class BaseLLM(ABC):
    @abstractmethod
    def answer(self, messages: list[Message], **kwargs: Any) -> Answer:
        pass
