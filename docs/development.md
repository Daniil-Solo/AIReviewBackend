## Гайд для разработчика

### Поднятие стенда

```bash
docker network create autoreviewer-network
docker compose up -d
```

### Установка зависимостей

Требуется установленный пакетный менеджер uv
```bash
uv sync
```

### Запуск всех линтеров

```bash
uv run ruff format src && uv run ruff check --fix src && uv run mypy src
```

### Миграции

```bash
uv run alembic revision --autogenerate -m "users"
```

```bash
uv run alembic upgrade
```

