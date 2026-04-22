from dependency_injector.wiring import Provide, inject

from src.application.ai_review.task_graph import PipelineStepEnum
from src.application.solutions.utils import get_workspace_id
from src.application.transactions.utils import charge_for_llm_call
from src.constants.ai_review import SolutionStatusEnum
from src.di.container import Container
from src.dto.solutions.solutions import SolutionUpdateDTO
from src.dto.transactions.metadata import LLMCallTransactionMetadataDTO
from src.infrastructure.ai.llm.interface import LLMInterface
from src.infrastructure.ai.prompt_builder.interface import PromptBuilderInterface
from src.infrastructure.logging import get_logger
from src.infrastructure.sqlalchemy.uow import UnitOfWork
from src.infrastructure.storage.artifact import SolutionArtifactStorage


logger = get_logger()


@inject
async def create_project_doc(
    solution_id: int,
    artifact_storage: SolutionArtifactStorage = Provide[Container.solution_artifact_storage],
    prompt_builder: PromptBuilderInterface = Provide[Container.prompt_builder],
    default_model: LLMInterface = Provide[Container.default_model],
    uow: UnitOfWork = Provide[Container.uow],
) -> None:
    project_tree = await artifact_storage.get_artifact(solution_id, PipelineStepEnum.PREPARE_PROJECT_TREE)
    project_content = await artifact_storage.get_artifact(solution_id, PipelineStepEnum.PREPARE_PROJECT_CONTENT)

    system_content = prompt_builder.build(prompt_path="project_doc/creating/system.tpl")
    user_content = prompt_builder.build(
        prompt_path="project_doc/creating/user.tpl", project_tree=project_tree, project_content=project_content
    )
    answer = await default_model.run(system_content, user_content)
    project_doc = answer.content
    await artifact_storage.save_artifact(solution_id, PipelineStepEnum.CREATE_PROJECT_DOC, project_doc)

    metadata = LLMCallTransactionMetadataDTO(
        solution_id=solution_id,
        task=PipelineStepEnum.CREATE_PROJECT_DOC,
        input_tokens=answer.input_tokens,
        output_tokens=answer.output_tokens,
    )
    async with uow.connection():
        workspace_id = await get_workspace_id(uow, solution_id)
        await charge_for_llm_call(uow, workspace_id, metadata)


@inject
async def generate_critic(
    solution_id: int,
    artifact_storage: SolutionArtifactStorage = Provide[Container.solution_artifact_storage],
    prompt_builder: PromptBuilderInterface = Provide[Container.prompt_builder],
    default_model: LLMInterface = Provide[Container.default_model],
    uow: UnitOfWork = Provide[Container.uow],
) -> None:
    project_doc = await artifact_storage.get_artifact(solution_id, PipelineStepEnum.CREATE_PROJECT_DOC)

    system_content = prompt_builder.build(prompt_path="project_doc/criticism/system.tpl", letter_prefix="A")
    user_content = prompt_builder.build(
        prompt_path="project_doc/criticism/user.tpl",
        project_doc=project_doc,
    )
    answer = await default_model.run(system_content, user_content)
    critic_doc = answer.content
    await artifact_storage.save_artifact(solution_id, PipelineStepEnum.GENERATE_CRITIC, critic_doc)

    metadata = LLMCallTransactionMetadataDTO(
        solution_id=solution_id,
        task=PipelineStepEnum.GENERATE_CRITIC,
        input_tokens=answer.input_tokens,
        output_tokens=answer.output_tokens,
    )
    async with uow.connection():
        workspace_id = await get_workspace_id(uow, solution_id)
        await charge_for_llm_call(uow, workspace_id, metadata)


@inject
async def resolve_gaps(
    solution_id: int,
    artifact_storage: SolutionArtifactStorage = Provide[Container.solution_artifact_storage],
    prompt_builder: PromptBuilderInterface = Provide[Container.prompt_builder],
    default_model: LLMInterface = Provide[Container.default_model],
    uow: UnitOfWork = Provide[Container.uow],
) -> None:
    project_tree = await artifact_storage.get_artifact(solution_id, PipelineStepEnum.PREPARE_PROJECT_TREE)
    project_content = await artifact_storage.get_artifact(solution_id, PipelineStepEnum.PREPARE_PROJECT_CONTENT)
    project_doc = await artifact_storage.get_artifact(solution_id, PipelineStepEnum.CREATE_PROJECT_DOC)
    critic_doc = await artifact_storage.get_artifact(solution_id, PipelineStepEnum.GENERATE_CRITIC)

    system_content = prompt_builder.build(prompt_path="project_doc/resolving/system.tpl", letter_prefix="A")
    user_content = prompt_builder.build(
        prompt_path="project_doc/resolving/user.tpl",
        project_tree=project_tree,
        project_content=project_content,
        project_doc=project_doc,
        critic_docs=[critic_doc],
    )
    answer = await default_model.run(system_content, user_content)
    resolve_doc = answer.content
    await artifact_storage.save_artifact(solution_id, PipelineStepEnum.RESOLVE_GAPS, resolve_doc)

    metadata = LLMCallTransactionMetadataDTO(
        solution_id=solution_id,
        task=PipelineStepEnum.RESOLVE_GAPS,
        input_tokens=answer.input_tokens,
        output_tokens=answer.output_tokens,
    )
    async with uow.connection():
        workspace_id = await get_workspace_id(uow, solution_id)
        await charge_for_llm_call(uow, workspace_id, metadata)


@inject
async def improve_doc(
    solution_id: int,
    artifact_storage: SolutionArtifactStorage = Provide[Container.solution_artifact_storage],
    prompt_builder: PromptBuilderInterface = Provide[Container.prompt_builder],
    default_model: LLMInterface = Provide[Container.default_model],
    uow: UnitOfWork = Provide[Container.uow],
) -> None:
    project_doc = await artifact_storage.get_artifact(solution_id, PipelineStepEnum.CREATE_PROJECT_DOC)
    resolve_doc = await artifact_storage.get_artifact(solution_id, PipelineStepEnum.RESOLVE_GAPS)

    system_content = prompt_builder.build(prompt_path="project_doc/improving/system.tpl")
    user_content = prompt_builder.build(
        prompt_path="project_doc/improving/user.tpl",
        project_doc=project_doc,
        resolve_doc=resolve_doc,
    )
    answer = await default_model.run(system_content, user_content)
    final_doc = answer.content
    await artifact_storage.save_artifact(solution_id, PipelineStepEnum.IMPROVE_DOC, final_doc)

    metadata = LLMCallTransactionMetadataDTO(
        solution_id=solution_id,
        task=PipelineStepEnum.IMPROVE_DOC,
        input_tokens=answer.input_tokens,
        output_tokens=answer.output_tokens,
    )
    async with uow.connection() as conn, conn.transaction():
        workspace_id = await get_workspace_id(uow, solution_id)
        await charge_for_llm_call(uow, workspace_id, metadata)
