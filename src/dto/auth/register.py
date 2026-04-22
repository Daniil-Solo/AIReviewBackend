from pydantic import Field

from src.dto.common import BaseDTO


class EmailRegistrationRequestDTO(BaseDTO):
    fullname: str = Field(description="Имя пользователя")
    email: str = Field(description="Электронная почта пользователя")
    password: str = Field(description="Пароль пользователя")


class EmailConfirmationRequestDTO(BaseDTO):
    email: str = Field(description="Электронная почта пользователя")
    code: str = Field(description="Код подтверждения")


class CodeInfoDTO(BaseDTO):
    """Хранится в Redis"""

    email: str = Field(description="Электронная почта пользователя")
    hashed_password: str = Field(description="Хэшированный пароль")
    code: str = Field(description="Код подтверждения")
    fullname: str = Field(description="Имя пользователя")
    attempts_count: int = Field(default=0, description="Количество попыток")
