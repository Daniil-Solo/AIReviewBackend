from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine


def create_engine(url: str, echo: bool = False) -> AsyncEngine:
    return create_async_engine(url, echo=echo)


def create_session_factory(engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
    return async_sessionmaker(engine, expire_on_commit=False)


async def check_database_connection(session_factory: async_sessionmaker[AsyncSession]) -> bool:
    async with session_factory() as session:
        await session.execute(text("SELECT 1"))
    return True
