from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class SolutionSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="SOLUTION_")

    MAX_UPLOADS_PER_TASK: int = Field(default=1, description="Макс. количество загрузок решений на задачу")
    CHECK_BALANCE_BEFORE_CREATING: bool = Field(default=True, description="Должен ли баланс быть положительным для начала проверки решения")