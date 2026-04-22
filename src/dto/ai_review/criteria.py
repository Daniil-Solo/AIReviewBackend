from pydantic import Field

from src.constants.ai_review import CriterionCheckStatusEnum, CriterionStageEnum
from src.dto.common import BaseDTO


class CriterionWithCommentsDTO(BaseDTO):
    """Является инпутом для модели"""

    id: int = Field(description="Идентификатор критерия")
    description: str = Field(description="Описание критерия")
    comments: list[str] = Field(default_factory=list, description="Комментарии модели с предыдущих этапов проверки")


class CriterionCheckDTO(BaseDTO):
    """Генерируется моделью"""

    id: int = Field(description="Идентификатор критерия")
    comment: str = Field(description="Комментарий о соблюдении критерии по представленным сведениям")
    status: CriterionCheckStatusEnum = Field(
        description="Можно ли на основании данных точно сказать, выполнен ли критерий, или требуется дополнительная информация"
    )
    is_passed: bool | None = Field(
        default=None, description="Факт выполнения критерия (имеет смысл только при status=SUFFICIENT)"
    )
