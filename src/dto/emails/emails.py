from pydantic import Field

from src.dto.common import BaseDTO
from src.settings import settings


class EmailMessageDTO(BaseDTO):
    # From
    from_email: str = Field(default=settings.email.FROM, description="От кого письмо")
    from_display_name: str = Field(default=settings.email.FROM_DISPLAY_NAME, description="От кого письмо")
    # Recipients
    to: list[str] = Field(description="Прямые получатели")
    cc: list[str] | None = Field(default=None, description="Те, кто будет в копии")
    bcc: list[str] | None = Field(default=None, description="Те, кто будет в скрытой копии")
    # Subject
    subject: str = Field(description="Тема письма")
    # Body
    html: str = Field(description="Текст письма в формате html")
    plain: str = Field(description="Текст письма в формате чистого текста")
