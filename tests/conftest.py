from collections.abc import AsyncGenerator
import logging
from typing import Any

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

        await conn.execute(f"CREATE DATABASE {test_db_name}")

        logger.info(f"Test database {test_db_name} created successfully")

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
    test_sync_url = f"postgresql://{settings.db.USER}:{settings.db.PASSWORD}@{settings.db.HOST}:{settings.db.PORT}/{test_database_name}"
    alembic_cfg = Config("alembic.ini")
    alembic_cfg.set_main_option("sqlalchemy.url", test_sync_url)

    command.downgrade(alembic_cfg, "base")
    command.upgrade(alembic_cfg, "head")

    yield

    command.downgrade(alembic_cfg, "base")


@pytest_asyncio.fixture
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


@pytest.fixture
def uow(container):
    uow = container.uow()
    return uow


@pytest.fixture
def init_settings():
    settings.logging.LOKI_ENABLED = False


@pytest_asyncio.fixture(scope="session")
async def client() -> AsyncGenerator[AsyncClient, Any]:
    app = create_app()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        yield client
