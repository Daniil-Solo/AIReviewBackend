# AI Review System

Платформа для автоматического ревью студенческих проектов и репозиториев с использованием LLM.

## Описание

Платформа анализирует код студенческих проектов, генерирует документацию проекта (ProjectDoc), проводит ревью по критериям и выносит итоговый вердикт.

## Технологический стек

- **API**: FastAPI, Uvicorn
- **Database**: PostgreSQL, SQLAlchemy Core, Alembic
- **AI**: OpenAI API
- **Linters**: Ruff, MyPy
- **CLI**: Click, Rich
- **Testing**: Pytest

## Компоненты

| Компонент | Описание | Ссылка |
|-----------|----------|--------|
| **Frontend** | Веб-интерфейс | [AIReviewFrontend](https://github.com/Daniil-Solo/AIReviewFrontend) |
| **Backend** | API сервер | Текущий репозиторий |

## Документация

| Раздел | Описание | Ссылка |
|-------|----------|--------|
| Архитектура | Общая архитектура системы | [`docs/architecture/architecture.md`](docs/architecture/architecture.md) |
| Модель данных | Сущности и связи | [`docs/architecture/data_model.md`](docs/architecture/data_model.md) |
| AI-пайплайн | Устройство ИИ для ревью | [`docs/architecture/ai.md`](docs/architecture/ai.md) |
| Разработка | Инструкции по запуску | [`docs/development.md`](docs/development.md) |

## Быстрый старт

```bash
bash scripts/gen_env.sh
docker compose up -d
```

## API Endpoints

- `POST /api/v1/auth/login` - Аутентификация
- `GET/POST /api/v1/users` - Управление пользователями
- `GET/POST /api/v1/workspaces` - Управление рабочими пространствами
- `GET/POST /api/v1/joins` - Присоединение к пространствам

## Требования

- Python 3.11+
- PostgreSQL 14+
- OpenAI API Key