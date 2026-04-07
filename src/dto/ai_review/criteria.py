from pydantic import Field

from src.constants.ai_review import CriterionConfidenceEnum
from src.dto.common import BaseDTO


class CriterionDTO(BaseDTO):
    id: int = Field(description="Идентификатор критерия")
    description: str = Field(description="Описание критерия")


class CriterionCheckDTO(BaseDTO):
    id: int = Field(description="Идентификатор критерия")
    comment: str = Field(description="Комментарий о соблюдении критерии по представленным сведениям")
    confidence: CriterionConfidenceEnum = Field(description="Оценка достаточности информации для точной оценки")
    value: float = Field(le=1, ge=0, description="Факт соблюдения критерия (1 или 0) или процент соблюдения (0...1)")
