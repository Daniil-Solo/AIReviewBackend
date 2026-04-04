# Конфигурация приложения

Актуально для любого проекта

## Критерии

### Для обращения к переменным окружения рекомендуется использовать pydantic_settings

Библиотека pydantic_settings позволяет создать классы для удобного обращения к переменным окружения

```python
from pydantic_settings import BaseSettings, SettingsConfigDict

class AuthConfig(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8')
    
    JWT_ALG: str
    JWT_SECRET: str
    JWT_EXP: int = 5

    SECURE_COOKIES: bool = True


auth_settings = AuthConfig()
```

### Для средних и больших проектов конфиг-класс из pydantic_settings разбит на несколько подконфигов

Это позволяет разбить все переменные окружения на группы


### Предоставлен пример набора переменных окружений

Обычно он находится в readme.md или env.example/example.env


