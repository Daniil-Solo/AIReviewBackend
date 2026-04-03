# AGENTS.md

## О проекте

Проект посвящен созданию бэкенда для платформы автоматического ревью проектов и репозиториев.

## Технологический стек

Статические анализаторы:
- ruff
- mypy
- bandit

Создание консольных команд:
- click - основной фреймворк
- rich - для красоты

Инъекция зависимостей:
- dependency-injector - управление зависимостями

Базы данных:
- sqlalchemy, alembic -
- asyncpg
- psycopg2-binary - драйвер PostgreSQL для миграций alembic


## Структура проекта

- src - весь исходный код проекта
  - dto - Data Transfer Objects для API и Service слоев
    - users/ - DTO для пользователей (UserCreateDTO, UserResponseDTO)
    - auth/ - DTO для аутентификации (UserLoginDTO, TokenDTO)
  - infrastructure - коннекторы к базе данных и внешним сервисам
    - auth/ - утилиты аутентификации (JWT, хеширование паролей)
    - dao/ - Data Access Object для работы с БД
    - di/ - контейнер dependency-injector
    - sqlalchemy/ - модели и таблицы БД
      - models.py - все таблицы SQLAlchemy Core
    - config.py - настройки приложения
    - database.py - подключение к БД
  - interfaces - различные точки входа в приложение
    - api - содержит эндпоинты API
      - auth/ - эндпоинты аутентификации
      - users/ - эндпоинты пользователей
      - internal/ - внутренние эндпоинты
      - dependencies.py - зависимости для FastAPI
      - exception_handlers.py - обработчики исключений
    - cli - содержит команды для запуска (локальное тестирование)
    - tasks - фоновые задачи
  - application - сервисы бизнес-логики
    - users/ - сервисы для работы с пользователями
    - exceptions.py - кастомные исключения
- docs - различная документация
  - architecture - основные mermaid-диаграммы проекта
    - ai.md - устройство AI-пайплайна для ревью
    - architecture.md - C4-диаграмма компонентов системы (уровень контейнеров)
    - data_model.md - ER-диаграмма (модель данных)
  - diploma - это тебе не нужно
  - usecases - содержит текстовое описание фичей с предложениями по реализации
  - development.md - основные инструкции для запуска проекта и линтеров


## Архитектурные слои

Проект использует слоистую архитектуру:

1. **Interfaces** - точка входа (API, CLI)
2. **Application** - бизнес-логика
3. **Application** - бизнес-логика
4. **Infrastructure** - реализация доступа к данным
5. **DTO** - объекты передачи данных

Зависимости: Interfaces → Services → Infrastructure/DAO
            Interfaces → DTO
            Services → DTO


## Запуск приложения

```bash
docker-compose up -d
```


## Важно

- Отвечай всегда на русском языке
- Для запуска команд всегда используй: `uv run ...'
- Для полей DTO всегда указывай описание и возможную валидацию: `Field(description="...")`