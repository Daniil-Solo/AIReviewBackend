from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class AuthSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="AUTH_")

    # jwt
    SECRET_KEY: str = Field(description="Ключ для хэширования пароля")
    ALGORITHM: str = Field(default="HS256", description="Алгоритм хэширования пароля")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=2 * 60, description="Время жизни токена доступа")

    CODE_CONFIRM_PREFIX: str = Field(default="code_confirm", description="Префикс ключа для регистрации")
    CODE_LENGTH: int = Field(default=6, description="Длина цифрового кода подтверждения")
    CONFIRM_TTL: int = Field(default=65, description="Время жизни кода подтверждения в секундах")
    MAX_CONFIRM_COUNT: int = Field(default=3, description="Максимальное количество попыток ввода кода")

    CODE_RESEND_PREFIX: str = Field(default="code_resend", description="Префикс ключа для учета переотправок кода")
    RESEND_TTL: int = Field(default=3600, description="Время жизни счётчика счетчика отправок кода для одного email")
    MAX_RESEND_COUNT: int = Field(default=3, description="Максимальное количество повторных отправок кода")
