# AGENTS.md

## О проекте

Проект посвящен созданию бэкенда для платформы автоматического ревью проектов и репозиториев.
Платформа анализирует код студентов, генерирует документацию проекта (ProjectDoc) через LLM,
проводит ревью по критериям и выносит итоговый вердикт.

## Технологический стек

Веб-фреймворк и сервер:
- fastapi - основной веб-фреймворк
- uvicorn - ASGI-сервер

Статические анализаторы:
- ruff - линтер
- mypy - проверка типов
- bandit - проверка безопасности

Создание консольных команд:
- click (asyncclick) - основной фреймворк
- rich - форматирование вывода в терминале

Инъекция зависимостей:
- dependency-injector - управление зависимостями

Базы данных:
- sqlalchemy (Core, не ORM) - работа с построение запросов
- alembic - миграции
- asyncpg - асинхронный драйвер PostgreSQL
- psycopg2-binary - синхронный драйвер PostgreSQL для миграций alembic

LLM и шаблоны:
- openai - клиент для OpenAI-совместимых API (Zveno AI, OpenRouter)
- jinja2 - шаблонизатор для промптов
- tiktoken - подсчёт токенов

Анализ кода:
- tree-sitter, tree-sitter-python - парсинг AST
- treeproject - извлечение структуры и контента проекта

Настройки и утилиты:
- pydantic-settings - управление настройками из env
- pyjwt - работа с JWT-токенами
- python-multipart - парсинг form-data


## Структура проекта

- src - весь исходный код проекта
  - application - сервисы бизнес-логики
    - auth/ - сервис аутентификации (логин)
    - health/ - сервис проверки здоровья
    - users/ - сервисы для работы с пользователями
    - project/ - пайплайн анализа проектов (в разработке)
    - exceptions.py - кастомные исключения (ApplicationError и др.)
  - di/ - контейнер dependency-injector
    - container.py - объявление всех зависимостей
  - dto - Data Transfer Objects для API и Service слоев
    - auth/ - DTO для аутентификации (UserLoginDTO, TokenDTO)
    - users/ - DTO для пользователей (UserCreateDTO, ShortUserDTO, UserResponseDTO)
  - infrastructure - коннекторы к базе данных и внешним сервисам
    - auth/ - утилиты аутентификации (JWT, хеширование паролей SHA256+salt)
      - jwt.py - создание и декодирование JWT
      - password.py - хеширование паролей
    - dao/ - Data Access Object для работы с БД
      - interfaces/ - абстрактные интерфейсы для конкретных сущностей
      - sqlalchemy/ - реализации интерфейсов на SQLAlchemy
    - llm/ - инфраструктура для работы с LLM
      - base.py - BaseLLM, Message, Answer
      - openai_like.py - OpenAI-совместимый клиент
      - file_writer.py - FileWriterLLM (для отладки)
    - sqlalchemy/ - модели и таблицы БД
      - models.py - все таблицы SQLAlchemy Core
      - engine.py - асинхронный engine и session factory
      - uow.py - UnitOfWork, агрегация всех DAO для одной сессии
  - interfaces - различные точки входа в приложение
    - api - содержит эндпоинты API
      - v1/ - эндпоинты версии v1
        - auth/ - аутентификация (POST /api/v1/auth/login)
        - users/ - управление пользователями (GET/POST /api/v1/users/*)
      - internal/ - внутренние эндпоинты
        - health.py - GET /api/internal/health
      - app.py - точка входа в приложение с объявлением FastAPI
      - dependencies.py - зависимости для FastAPI (get_current_user)
      - error_status_mapping.py - маппинг ошибок из бизнес-слоя на HTTP-коды
    - cli - содержит команды для запуска (локальное тестирование, в разработке)
    - tasks - фоновые задачи (заглушка)
  - settings/ - агрегация настроек
- alembic/ - миграции базы данных
- docs - документация
  - architecture/ - основные mermaid-диаграммы проекта
    - ai.md - устройство AI-пайплайна для ревью
    - architecture.md - C4-диаграмма компонентов системы (уровень контейнеров)
    - data_model.md - ER-диаграмма (модель данных, 12 сущностей)
  - usecases/ - текстовое описание фичей с предложениями по реализации
  - development.md - инструкции для запуска проекта и линтеров
  - diploma/ - не актуально
  - examples/ - не актуально
  - ui/ - UI-документация
- extra/ - промпты, критерии для ревью
- experiments/ - не актуально


## Архитектурные слои

Проект использует слоистую архитектуру:

1. **Interfaces** - точка входа (API, CLI)
2. **Application** - бизнес-логика
3. **Infrastructure** - реализация доступа к данным и внешним сервисам
4. **DTO** - объекты передачи данных между слоями


## Дополнительные сведения

- `docs/development.md` - инструкции для запуска проекта, линтеров, миграций


## Важно

- Отвечай всегда на русском языке
- Для запуска команд всегда используй: `uv run ...`
- Для полей DTO всегда указывай описание и возможную валидацию: `Field(description="...")`
- SQLAlchemy используется в режиме Core (императивные таблицы), не ORM; запросы в DAO также составляются с помощью Core
- Всегда реализиуй эндпоинты, дао, сервисные функции по аналогии с уже существующими(src/infrastructure/dao/users, src/interfaces/api/v1/users, )
