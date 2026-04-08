from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class AISettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="AI_")

    LLM_API_ENDPOINT: str = Field(description="OpenAI-подобный путь для обращения к LLM}", examples=["https://openrouter.ai/api/v1"])
    LLM_API_KEY: str = Field(description="Ключ доступа", examples=["sk-***"])
    LLM_DEFAULT_MODEL: str = Field(description="Ключ доступа", examples=["qwen/qwen3-235b-a22b-2507"])
