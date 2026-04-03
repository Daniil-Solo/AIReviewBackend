import datetime
import re

from pydantic import BaseModel, Field, field_validator


class UserCreateDTO(BaseModel):
    fullname: str = Field(min_length=1, max_length=255, description="Полное имя пользователя")
    email: str = Field(description="Электронная почта пользователя")
    password: str = Field(min_length=8, description="Пароль пользователя")

    @field_validator("password", mode="after")
    @classmethod
    def validate_password(cls, v: str) -> str:
        if not re.search(r"\d", v):
            raise ValueError("Password must contain at least one digit")
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", v):
            raise ValueError("Password must contain at least one special character")
        return v


class ShortUserDTO(BaseModel):
    id: int
    email: str
    fullname: str
    is_admin: bool


class UserResponseDTO(ShortUserDTO):
    is_verified: bool
    created_at: datetime.datetime

    def as_short(self) -> ShortUserDTO:
        return ShortUserDTO(**self.model_dump(by_alias=True))
