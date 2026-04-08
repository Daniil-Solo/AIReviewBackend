from typing import Literal
from pydantic import Field

from src.dto.common import BaseDTO


class AIAnswerDTO(BaseDTO):
    content: str | None = None
    in_tokens: int | None = None
    out_tokens: int | None = None


class InputMessageDTO(BaseDTO):
    role: Literal["system", "user", "assistant"] = Field(description="Роль")
    content: str = Field(description="Текст ")