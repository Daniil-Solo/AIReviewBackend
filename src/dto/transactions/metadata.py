from pydantic import Field

from src.dto.common import BaseDTO


class LLMCallTransactionMetadataDTO(BaseDTO):
    solution_id: int | None = None
    input_tokens: int = Field(description="Количество входных токенов")
    output_tokens: int = Field(description="Количество выходных токенов")
    task: str = Field(description="Задача (шаг ai-пайплайна или что-то другое)")
