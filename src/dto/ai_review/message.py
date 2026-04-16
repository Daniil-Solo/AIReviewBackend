from typing import Literal

from pydantic import Field

from src.dto.common import BaseDTO


class AIAnswerDTO(BaseDTO):
    content: str
    input_tokens: int
    output_tokens: int


class InputMessageDTO(BaseDTO):
    role: Literal["system", "user", "assistant"] = Field(description="Роль")
    content: str = Field(description="Текст ")
