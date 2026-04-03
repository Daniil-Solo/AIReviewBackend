from sqlalchemy.ext.asyncio import AsyncSession

from src.infrastructure.dao.sqlalchemy.users import SQLAlchemyUsersDAO
from src.infrastructure.sqlalchemy.engine import async_session_maker


class UnitOfWork:
    def __init__(self, session_factory: async_session_maker):
        self._session_factory = session_factory
        self._session: AsyncSession | None = None
        # DAO
        self.users: SQLAlchemyUsersDAO | None = None

    async def __aenter__(self):
        self._session = self._session_factory()
        self.users = SQLAlchemyUsersDAO(self._session)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if exc_type is None:
            await self._session.commit()
        else:
            await self._session.rollback()
        await self._session.close()
        self._session = None
        self.users = None
