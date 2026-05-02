from dependency_injector import containers, providers
from redis.asyncio import Redis

from src.constants.emails import EmailSenderTypeEnum
from src.infrastructure.ai.llm.interface import LLMInterface
from src.infrastructure.ai.llm.openai_like import OpenAILikeLLM
from src.infrastructure.ai.prompt_builder.interface import PromptBuilderInterface
from src.infrastructure.ai.prompt_builder.jinja2 import Jinja2PromptBuilder
from src.infrastructure.dao.criteria.sqlalchemy import SQLAlchemyCriteriaDAO
from src.infrastructure.dao.custom_models.sqlalchemy import SQLAlchemyCustomModelsDAO
from src.infrastructure.dao.pipeline_tasks.sqlalchemy import SQLAlchemyPipelineTasksDAO
from src.infrastructure.dao.registrations.interface import RegistrationsFlow
from src.infrastructure.dao.registrations.redis import RedisRegistrationsFlow
from src.infrastructure.dao.solution_criteria_checks.sqlalchemy import SQLAlchemySolutionCriteriaChecksDAO
from src.infrastructure.dao.solutions.sqlalchemy import SQLAlchemySolutionsDAO
from src.infrastructure.dao.task_criteria.sqlalchemy import SQLAlchemyTaskCriteriaDAO
from src.infrastructure.dao.task_steps_models.sqlalchemy import SQLAlchemyTaskStepsModelsDAO
from src.infrastructure.dao.tasks.sqlalchemy import SQLAlchemyTasksDAO
from src.infrastructure.dao.transactions.sqlalchemy import SQLAlchemyTransactionsDAO
from src.infrastructure.dao.users.sqlalchemy import SQLAlchemyUsersDAO
from src.infrastructure.dao.workspace_join_rules.sqlalchemy import SQLAlchemyWorkspaceJoinRulesDAO
from src.infrastructure.dao.workspace_members.sqlalchemy import SQLAlchemyWorkspaceMembersDAO
from src.infrastructure.dao.workspaces.sqlalchemy import SQLAlchemyWorkspacesDAO
from src.infrastructure.email_sender.disabled import DisabledEmailSender
from src.infrastructure.email_sender.interface import EmailSenderInterface
from src.infrastructure.email_sender.maileroo import MailerooEmailSender
from src.infrastructure.email_sender.smtp import SmtpEmailSender
from src.infrastructure.email_templater.interface import EmailTemplaterInterface
from src.infrastructure.email_templater.jinja2 import Jinja2EmailTemplater
from src.infrastructure.encryptor.fernet import FernetEncryptor
from src.infrastructure.encryptor.interface import BaseEncryptor
from src.infrastructure.logs_sender.init_logs_sender import init_logs_sender
from src.infrastructure.rate_limiter.rate_limiter import RateLimiter
from src.infrastructure.redis.client import init_redis_client
from src.infrastructure.solution_artifact_storage.interface import SolutionArtifactStorage
from src.infrastructure.solution_artifact_storage.s3 import S3SolutionArtifactStorage
from src.infrastructure.solution_storage.interface import SolutionStorage
from src.infrastructure.solution_storage.s3 import S3SolutionStorage
from src.infrastructure.sqlalchemy.engine import create_engine, create_session_factory
from src.infrastructure.sqlalchemy.uow import UnitOfWork
from src.settings import ROOT_DIR, settings


def _get_email_sender() -> EmailSenderInterface:  # type: ignore[misc]
    email_type = settings.email.TYPE
    if email_type == EmailSenderTypeEnum.MAILEROO:
        return MailerooEmailSender(token=settings.email.MAILEROO_API_KEY)  # type: ignore[arg-type]
    if email_type == EmailSenderTypeEnum.SMTP:
        return SmtpEmailSender(
            host=settings.email.SMTP_HOST,  # type: ignore[arg-type]
            port=settings.email.SMTP_PORT,  # type: ignore[arg-type]
            user=settings.email.SMTP_USER,  # type: ignore[arg-type]
            password=settings.email.SMTP_PASSWORD,  # type: ignore[arg-type]
            use_tls=settings.email.SMTP_USE_TLS,  # type: ignore[arg-type]
        )
    return DisabledEmailSender()


class Container(containers.DeclarativeContainer):
    engine = providers.Singleton(
        create_engine, url=providers.Callable(lambda: settings.db.url), echo=settings.db.SQL_ECHO
    )

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
    solutions_dao = providers.Factory(lambda: SQLAlchemySolutionsDAO)
    solution_criteria_checks_dao = providers.Factory(lambda: SQLAlchemySolutionCriteriaChecksDAO)
    pipeline_tasks_dao = providers.Factory(lambda: SQLAlchemyPipelineTasksDAO)
    transactions_dao = providers.Factory(lambda: SQLAlchemyTransactionsDAO)
    custom_models_dao = providers.Factory(lambda: SQLAlchemyCustomModelsDAO)
    task_steps_models_dao = providers.Factory(lambda: SQLAlchemyTaskStepsModelsDAO)

    redis_client = providers.Resource[Redis](init_redis_client)
    registrations_flow = providers.Factory[RegistrationsFlow](
        RedisRegistrationsFlow,
        redis=redis_client,
        prefix=settings.auth.CODE_CONFIRM_PREFIX,
        ttl=settings.auth.CONFIRM_TTL,
        max_count=settings.auth.MAX_CONFIRM_COUNT,
    )
    resend_code_rate_limiter = providers.Factory(
        RateLimiter,
        redis=redis_client,
        prefix=settings.auth.CODE_RESEND_PREFIX,
        ttl=settings.auth.RESEND_TTL,
        max_count=settings.auth.MAX_RESEND_COUNT,
    )

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
        solutions_dao_factory=solutions_dao,
        solution_criteria_checks_dao_factory=solution_criteria_checks_dao,
        pipeline_tasks_dao_factory=pipeline_tasks_dao,
        transactions_dao_factory=transactions_dao,
        custom_models_dao_factory=custom_models_dao,
        task_steps_models_dao_factory=task_steps_models_dao,
    )

    encryptor = providers.Singleton[BaseEncryptor](FernetEncryptor, encryption_key=settings.security.ENCRYPTION_KEY)

    solution_storage = providers.Factory[SolutionStorage](
        S3SolutionStorage,
        endpoint=settings.storage.ENDPOINT,
        access_key=settings.storage.ACCESS_KEY,
        secret_key=settings.storage.SECRET_KEY,
        bucket=settings.storage.SOLUTIONS_BUCKET,
        use_ssl=settings.storage.USE_SSL,
    )

    solution_artifact_storage = providers.Factory[SolutionArtifactStorage](
        S3SolutionArtifactStorage,
        endpoint=settings.storage.ENDPOINT,
        access_key=settings.storage.ACCESS_KEY,
        secret_key=settings.storage.SECRET_KEY,
        bucket=settings.storage.SOLUTION_ARTIFACTS_BUCKET,
        use_ssl=settings.storage.USE_SSL,
    )

    logs_sender = providers.Resource(init_logs_sender)

    email_sender = providers.Factory[EmailSenderInterface](_get_email_sender)
    email_templater = providers.Factory[EmailTemplaterInterface](
        Jinja2EmailTemplater, templates_dir_path=ROOT_DIR / "src" / "email_templates"
    )

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
            "src.application.solutions",
            "src.application.transactions",
            "src.application.custom_models",
        ]
    )
    await container.init_resources()  # type: ignore[misc]
    return container


async def shutdown_container(container: Container) -> None:
    await container.shutdown_resources()  # type: ignore[misc]
    engine = container.engine()
    await engine.dispose()
