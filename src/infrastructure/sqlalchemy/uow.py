from collections.abc import AsyncGenerator, Callable
from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import AsyncSession

from src.infrastructure.dao.criteria.interface import CriteriaDAO
from src.infrastructure.dao.pipeline_tasks.interface import PipelineTasksDAO
from src.infrastructure.dao.solutions.interface import SolutionsDAO
from src.infrastructure.dao.task_criteria.interface import TaskCriteriaDAO
from src.infrastructure.dao.tasks.interface import TasksDAO
from src.infrastructure.dao.transactions.interface import TransactionsDAO
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
        criteria_dao_factory: Callable[[AsyncSession], CriteriaDAO],
        tasks_dao_factory: Callable[[AsyncSession], TasksDAO],
        task_criteria_dao_factory: Callable[[AsyncSession], TaskCriteriaDAO],
        solutions_dao_factory: Callable[[AsyncSession], SolutionsDAO],
        pipeline_tasks_dao_factory: Callable[[AsyncSession], PipelineTasksDAO],
        transactions_dao_factory: Callable[[AsyncSession], TransactionsDAO],
    ) -> None:
        self._session_factory = session_factory
        self._session: AsyncSession | None = None
        # dao factory
        self._users_dao_factory = users_dao_factory
        self._workspaces_dao_factory = workspaces_dao_factory
        self._workspace_members_dao_factory = workspace_members_dao_factory
        self._workspace_join_rules_dao_factory = workspace_join_rules_dao_factory
        self._criteria_dao_factory = criteria_dao_factory
        self._tasks_dao_factory = tasks_dao_factory
        self._task_criteria_dao_factory = task_criteria_dao_factory
        self._solutions_dao_factory = solutions_dao_factory
        self._pipeline_tasks_dao_factory = pipeline_tasks_dao_factory
        self._transactions_dao_factory = transactions_dao_factory
        # dao
        self._users: UsersDAO | None = None
        self._workspaces: WorkspacesDAO | None = None
        self._workspace_members: WorkspaceMembersDAO | None = None
        self._workspace_join_rules: WorkspaceJoinRulesDAO | None = None
        self._criteria: CriteriaDAO | None = None
        self._tasks: TasksDAO | None = None
        self._task_criteria: TaskCriteriaDAO | None = None
        self._solutions: SolutionsDAO | None = None
        self._pipeline_tasks: PipelineTasksDAO | None = None
        self._transactions: TransactionsDAO | None = None

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
                self._criteria = None
                self._tasks = None
                self._task_criteria = None
                self._solutions = None
                self._pipeline_tasks = None
                self._transactions = None

    @property
    def session(self) -> AsyncSession:
        if self._session is None:
            raise RuntimeError("Session not initialized. Use connection() context manager.")
        return self._session

    @property
    def users(self) -> UsersDAO:
        if self._users is None:
            self._users = self._users_dao_factory(self._session)  # type: ignore[assignment]
        return self._users

    @property
    def workspaces(self) -> WorkspacesDAO:
        if self._workspaces is None:
            self._workspaces = self._workspaces_dao_factory(self._session)  # type: ignore[assignment]
        return self._workspaces

    @property
    def workspace_members(self) -> WorkspaceMembersDAO:
        if self._workspace_members is None:
            self._workspace_members = self._workspace_members_dao_factory(self._session)  # type: ignore[assignment]
        return self._workspace_members

    @property
    def workspace_join_rules(self) -> WorkspaceJoinRulesDAO:
        if self._workspace_join_rules is None:
            self._workspace_join_rules = self._workspace_join_rules_dao_factory(self._session)  # type: ignore[assignment]
        return self._workspace_join_rules

    @property
    def criteria(self) -> CriteriaDAO:
        if self._criteria is None:
            self._criteria = self._criteria_dao_factory(self._session)  # type: ignore[assignment]
        return self._criteria

    @property
    def tasks(self) -> TasksDAO:
        if self._tasks is None:
            self._tasks = self._tasks_dao_factory(self._session)  # type: ignore[assignment]
        return self._tasks

    @property
    def task_criteria(self) -> TaskCriteriaDAO:
        if self._task_criteria is None:
            self._task_criteria = self._task_criteria_dao_factory(self._session)  # type: ignore[assignment]
        return self._task_criteria

    @property
    def solutions(self) -> SolutionsDAO:
        if self._solutions is None:
            self._solutions = self._solutions_dao_factory(self._session)  # type: ignore[assignment]
        return self._solutions

    @property
    def pipeline_tasks(self) -> PipelineTasksDAO:
        if self._pipeline_tasks is None:
            self._pipeline_tasks = self._pipeline_tasks_dao_factory(self._session)  # type: ignore[assignment]
        return self._pipeline_tasks

    @property
    def transactions(self) -> TransactionsDAO:
        if self._transactions is None:
            self._transactions = self._transactions_dao_factory(self._session)  # type: ignore[assignment]
        return self._transactions
