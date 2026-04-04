from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class JWTSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="JWT_")

    SECRET_KEY: str = Field(description="Ключ для хэширования пароля")
    ALGORITHM: str = Field(default="HS256", description="Алгоритм хэширования пароля")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=2 * 60, description="Время жизни токена доступа")
