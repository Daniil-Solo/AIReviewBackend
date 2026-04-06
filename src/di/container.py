from dependency_injector import containers, providers

from src.infrastructure.dao.users.sqlalchemy import SQLAlchemyUsersDAO
from src.infrastructure.dao.workspace_join_rules.sqlalchemy import SQLAlchemyWorkspaceJoinRulesDAO
from src.infrastructure.dao.workspace_members.sqlalchemy import SQLAlchemyWorkspaceMembersDAO
from src.infrastructure.dao.workspaces.sqlalchemy import SQLAlchemyWorkspacesDAO
from src.infrastructure.logs_sender.init_logs_sender import init_logs_sender
from src.infrastructure.sqlalchemy.engine import create_engine, create_session_factory
from src.infrastructure.sqlalchemy.uow import UnitOfWork
from src.settings import settings


class Container(containers.DeclarativeContainer):
    engine = providers.Singleton(create_engine, url=settings.db.url, echo=settings.db.SQL_ECHO)

    session_factory = providers.Singleton(
        create_session_factory,
        engine=engine,
    )

    users_dao = providers.Factory(lambda: SQLAlchemyUsersDAO)
    workspaces_dao = providers.Factory(lambda: SQLAlchemyWorkspacesDAO)
    workspace_members_dao = providers.Factory(lambda: SQLAlchemyWorkspaceMembersDAO)
    workspace_join_rules_dao = providers.Factory(lambda: SQLAlchemyWorkspaceJoinRulesDAO)

    uow = providers.Factory(
        UnitOfWork,
        session_factory=session_factory,
        users_dao_factory=users_dao,
        workspaces_dao_factory=workspaces_dao,
        workspace_members_dao_factory=workspace_members_dao,
        workspace_join_rules_dao_factory=workspace_join_rules_dao,
    )

    logs_sender = providers.Resource(init_logs_sender)


async def init_container() -> Container:
    container = Container()
    container.wire(
        packages=[
            "src.application.auth",
            "src.application.health",
            "src.application.users",
            "src.application.workspaces",
        ]
    )
    await container.init_resources()
    return container


async def shutdown_container(container: Container) -> None:
    await container.shutdown_resources()
    engine = container.engine()
    await engine.dispose()
