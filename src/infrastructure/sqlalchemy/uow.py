from collections.abc import Callable
import types

from sqlalchemy.ext.asyncio import AsyncSession

from src.infrastructure.dao.interfaces.users import UsersDAO


class UnitOfWork:
    def __init__(
        self,
        session_factory: Callable[[], AsyncSession],
        users_dao_factory: Callable[[AsyncSession], UsersDAO],
    ) -> None:
        self._session_factory = session_factory
        self._users_dao_factory = users_dao_factory
        self._session: AsyncSession | None = None
        self._users: UsersDAO | None = None

    @property
    def users(self) -> UsersDAO:
        if self._users is None:
            assert self._session is not None
            self._users = self._users_dao_factory(self._session)
        return self._users

    @property
    def session(self) -> AsyncSession:
        return self._session

    async def __aenter__(self) -> AsyncSession:
        self._session = self._session_factory()
        return self

    async def __aexit__(
        self, exc_type: type[BaseException] | None, exc_val: BaseException | None, exc_tb: types.TracebackType | None
    ) -> None:
        if exc_type is None:
            await self._session.commit()
        else:
            await self._session.rollback()
        await self._session.close()
        self._session = None
        self._users = None

    async def commit(self) -> None:
        if self._session is not None:
            await self._session.commit()
