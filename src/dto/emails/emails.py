from pydantic import Field

from src.dto.common import BaseDTO
from src.settings import settings


class EmailMessageDTO(BaseDTO):
    # Recipients
    to: list[str] = Field(description="Прямые получатели")
    cc: list[str] | None = Field(default=None, description="Те, кто будет в копии")
    bcc: list[str] | None = Field(default=None, description="Те, кто будет в скрытой копии")
    # Subject
    subject: str = Field(description="Тема письма")
    # Body
    html: str = Field(description="Текст письма в формате html")
    plain: str = Field(description="Текст письма в формате чистого текста")
