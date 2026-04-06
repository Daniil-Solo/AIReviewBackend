from collections.abc import AsyncGenerator, Callable
from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import AsyncSession

from src.infrastructure.dao.users.interface import UsersDAO
from src.infrastructure.dao.workspace_join_rules.interface import WorkspaceJoinRulesDAO
from src.infrastructure.dao.workspace_members.interface import WorkspaceMembersDAO
from src.infrastructure.dao.workspaces.interface import WorkspacesDAO


class Connection:
    def __init__(self, session: AsyncSession):
        self._session = session

    @asynccontextmanager
    async def transaction(self) -> AsyncGenerator[None, None]:
        async with self._session.begin_nested():
            yield


class UnitOfWork:
    def __init__(
        self,
        session_factory: Callable[[], AsyncSession],
        users_dao_factory: Callable[[AsyncSession], UsersDAO],
        workspaces_dao_factory: Callable[[AsyncSession], WorkspacesDAO],
        workspace_members_dao_factory: Callable[[AsyncSession], WorkspaceMembersDAO],
        workspace_join_rules_dao_factory: Callable[[AsyncSession], WorkspaceJoinRulesDAO],
    ) -> None:
        self._session_factory = session_factory
        self._session: AsyncSession | None = None
        # dao factory
        self._users_dao_factory = users_dao_factory
        self._workspaces_dao_factory = workspaces_dao_factory
        self._workspace_members_dao_factory = workspace_members_dao_factory
        self._workspace_join_rules_dao_factory = workspace_join_rules_dao_factory
        # dao
        self._users: UsersDAO | None = None
        self._workspaces: WorkspacesDAO | None = None
        self._workspace_members: WorkspaceMembersDAO | None = None
        self._workspace_join_rules: WorkspaceJoinRulesDAO | None = None

    @asynccontextmanager
    async def connection(self) -> AsyncGenerator[Connection, None]:
        if self._session is None:
            self._session = self._session_factory()
        try:
            yield Connection(self._session)
            await self._session.commit()
        except Exception:
            if self._session is not None:
                await self._session.rollback()
            raise
        finally:
            if self._session is not None:
                await self._session.close()
                self._session = None
                self._users = None
                self._workspaces = None
                self._workspace_members = None
                self._workspace_join_rules = None

    @property
    def users(self) -> UsersDAO:
        if self._users is None:
            self._users = self._users_dao_factory(self._session)
        return self._users

    @property
    def workspaces(self) -> WorkspacesDAO:
        if self._workspaces is None:
            self._workspaces = self._workspaces_dao_factory(self._session)
        return self._workspaces

    @property
    def workspace_members(self) -> WorkspaceMembersDAO:
        if self._workspace_members is None:
            self._workspace_members = self._workspace_members_dao_factory(self._session)
        return self._workspace_members

    @property
    def workspace_join_rules(self) -> WorkspaceJoinRulesDAO:
        if self._workspace_join_rules is None:
            self._workspace_join_rules = self._workspace_join_rules_dao_factory(self._session)
        return self._workspace_join_rules

    @property
    def session(self) -> AsyncSession:
        return self._session
