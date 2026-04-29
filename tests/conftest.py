from collections.abc import AsyncGenerator
import logging
from typing import Any
from unittest.mock import AsyncMock, patch

from alembic import command
from alembic.config import Config
import asyncpg
from httpx import ASGITransport, AsyncClient
import pytest
import pytest_asyncio
from sqlalchemy import text

from src.di.container import init_container, shutdown_container
from src.infrastructure.sqlalchemy.models import ALL_TABLES
from src.interfaces.api.app import create_app
from src.settings import settings


logger = logging.getLogger(__name__)


@pytest_asyncio.fixture(scope="session")
async def test_database_name():
    conn = None
    test_db_name = "test_autoreviewer"

    try:
        conn = await asyncpg.connect(settings.db.sync_url)

        exists = await conn.fetchval("SELECT 1 FROM pg_database WHERE datname = $1", test_db_name)
        if exists:
            await conn.execute(f"DROP DATABASE {test_db_name}")

        await conn.execute(f"CREATE DATABASE {test_db_name}")

        logger.info(f"Test database {test_db_name} created successfully")
        settings.db.DB = test_db_name

        yield test_db_name

    finally:
        if conn:
            try:
                await conn.execute(f"DROP DATABASE IF EXISTS {test_db_name}")
                await conn.close()
                logger.info(f"Test database {test_db_name} dropped")
            except Exception as e:
                logger.error(f"Failed to drop test database: {e}")


@pytest_asyncio.fixture(scope="session", autouse=True)
async def run_migrations(test_database_name):
    alembic_cfg = Config("alembic.ini")
    alembic_cfg.set_main_option("sqlalchemy.url", settings.db.sync_url)

    command.downgrade(alembic_cfg, "base")
    command.upgrade(alembic_cfg, "head")

    yield

    command.downgrade(alembic_cfg, "base")


@pytest_asyncio.fixture(scope="function")
async def container(run_migrations):
    container = await init_container()

    engine = container.engine()
    async with engine.begin() as conn:
        for table in ALL_TABLES:
            await conn.execute(text(f"TRUNCATE TABLE {table.name} CASCADE"))

    try:
        yield container
    finally:
        await shutdown_container(container)


@pytest_asyncio.fixture(scope="function")
def uow(container):
    uow = container.uow()
    return uow


@pytest.fixture(scope="session", autouse=True)
def init_settings():
    settings.logging.LOKI_ENABLED = False
    settings.redis.ENABLED = False


@pytest_asyncio.fixture(scope="session")
async def client() -> AsyncGenerator[AsyncClient, Any]:
    app = create_app()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        yield client


@pytest.fixture(autouse=True)
def mock_validate_custom_model():
    with patch("src.application.custom_models.custom_models.validate_custom_model", new_callable=AsyncMock) as mock:
        mock.return_value = None
        yield mock
