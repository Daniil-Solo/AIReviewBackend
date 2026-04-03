from sqlalchemy import text
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from src.settings import settings


engine = create_async_engine(settings.db.url, echo=False)
async_session_maker = async_sessionmaker(engine, expire_on_commit=False)


async def check_database_connection() -> bool:
    async with async_session_maker() as session:
        await session.execute(text("SELECT 1"))
    return True
