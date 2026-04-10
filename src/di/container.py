from dependency_injector import containers, providers

from src.infrastructure.ai.llm.interface import LLMInterface
from src.infrastructure.ai.llm.openai_like import OpenAILikeLLM
from src.infrastructure.ai.prompt_builder.interface import PromptBuilderInterface
from src.infrastructure.ai.prompt_builder.jinja2 import Jinja2PromptBuilder
from src.infrastructure.dao.criteria.sqlalchemy import SQLAlchemyCriteriaDAO
from src.infrastructure.dao.task_criteria.sqlalchemy import SQLAlchemyTaskCriteriaDAO
from src.infrastructure.dao.tasks.sqlalchemy import SQLAlchemyTasksDAO
from src.infrastructure.dao.users.sqlalchemy import SQLAlchemyUsersDAO
from src.infrastructure.dao.workspace_join_rules.sqlalchemy import SQLAlchemyWorkspaceJoinRulesDAO
from src.infrastructure.dao.workspace_members.sqlalchemy import SQLAlchemyWorkspaceMembersDAO
from src.infrastructure.dao.workspaces.sqlalchemy import SQLAlchemyWorkspacesDAO
from src.infrastructure.logs_sender.init_logs_sender import init_logs_sender
from src.infrastructure.sqlalchemy.engine import create_engine, create_session_factory
from src.infrastructure.sqlalchemy.uow import UnitOfWork
from src.settings import ROOT_DIR, settings


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
    criteria_dao = providers.Factory(lambda: SQLAlchemyCriteriaDAO)
    tasks_dao = providers.Factory(lambda: SQLAlchemyTasksDAO)
    task_criteria_dao = providers.Factory(lambda: SQLAlchemyTaskCriteriaDAO)

    uow = providers.Factory(
        UnitOfWork,
        session_factory=session_factory,
        users_dao_factory=users_dao,
        workspaces_dao_factory=workspaces_dao,
        workspace_members_dao_factory=workspace_members_dao,
        workspace_join_rules_dao_factory=workspace_join_rules_dao,
        criteria_dao_factory=criteria_dao,
        tasks_dao_factory=tasks_dao,
        task_criteria_dao_factory=task_criteria_dao,
    )

    logs_sender = providers.Resource(init_logs_sender)
    prompt_builder = providers.Singleton[PromptBuilderInterface](
        Jinja2PromptBuilder, prompts_dir_path=ROOT_DIR / "ai_review" / "prompts"
    )
    default_model = providers.Factory[LLMInterface](
        OpenAILikeLLM,
        base_url=settings.ai.LLM_API_ENDPOINT,
        api_key=settings.ai.LLM_API_KEY,
        model=settings.ai.LLM_DEFAULT_MODEL,
        common_parameters={"stream": False, "temperature": 0.1},
    )


async def init_container() -> Container:
    container = Container()
    container.wire(
        packages=[
            "src.application.auth",
            "src.application.health",
            "src.application.users",
            "src.application.workspaces",
            "src.application.criteria",
            "src.application.ai_review",
            "src.application.tasks",
        ]
    )
    await container.init_resources()
    return container


async def shutdown_container(container: Container) -> None:
    await container.shutdown_resources()
    engine = container.engine()
    await engine.dispose()
