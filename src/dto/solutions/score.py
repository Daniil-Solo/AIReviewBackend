from pydantic import Field

from src.dto.common import BaseDTO


class SolutionScoreDTO(BaseDTO):
    score: int = Field(description="Взвешенный балл (0-100)", ge=0, le=100)
    total_criteria: int = Field(description="Общее количество критериев")
    passed_criteria: int = Field(description="Количество удовлетворенных критериев")
