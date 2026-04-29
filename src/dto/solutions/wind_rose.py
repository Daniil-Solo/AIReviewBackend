from pydantic import Field

from src.dto.common import BaseDTO


class WindRosePointDTO(BaseDTO):
    tag: str = Field(description="Тег критерия")
    value: float = Field(description="Процент прохождения (0.0 - 1.0)")
    count: int = Field(description="Количество критериев в группе")
