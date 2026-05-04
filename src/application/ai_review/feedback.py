from dependency_injector.wiring import Provide, inject

from src.application.ai_review.task_graph import PipelineStepEnum
from src.application.custom_models.utils import get_llm_for_step
from src.application.solutions.common import check_solution_permissions
from src.application.solutions.utils import get_workspace_id
from src.application.transactions.utils import charge_for_llm_call
from src.di.container import Container
from src.dto.common import BaseDTO
from src.dto.criteria import CriterionFiltersDTO
from src.dto.solutions.solutions import SolutionUpdateDTO
from src.dto.users.user import ShortUserDTO
from src.infrastructure.ai.prompt_builder.interface import PromptBuilderInterface
from src.infrastructure.logging import get_logger
from src.infrastructure.solution_artifact_storage.interface import SolutionArtifactStorage
from src.infrastructure.sqlalchemy.uow import UnitOfWork


logger = get_logger()


class CriterionInFeedbackDTO(BaseDTO):
    description: str
    comment: str
    is_passed: bool | None


@inject
async def generate_feedback(
    solution_id: int,
    user: ShortUserDTO,
    artifact_storage: SolutionArtifactStorage = Provide[Container.solution_artifact_storage],
    prompt_builder: PromptBuilderInterface = Provide[Container.prompt_builder],
    uow: UnitOfWork = Provide[Container.uow],
) -> str:
    project_doc = await artifact_storage.get_artifact(solution_id, PipelineStepEnum.VALIDATE_PROJECT_DOC)

    async with uow.connection():
        solution = await check_solution_permissions(uow, user.id, solution_id, allow_author=False)
        task = await uow.tasks.get_by_id(solution.task_id)
        checks = await uow.solution_criteria_checks.get_latest_by_solution(solution_id)
        task_criterion_ids = [ch.task_criterion_id for ch in checks]
        task_criteria = await uow.task_criteria.get_by_ids(task_criterion_ids)
        task_criterion_id_to_criterion_id_map = {tc.id: tc.criterion_id for tc in task_criteria}
        criteria = await uow.criteria.get_list(
            CriterionFiltersDTO(ids=list(task_criterion_id_to_criterion_id_map.values()), workspace_id=task.workspace_id, task_id=task.id)
        )
        criterion_id_to_description_map = {criterion.id: criterion.description for criterion in criteria}
        criterion_id_to_prompt_map = {criterion.id: criterion.prompt for criterion in criteria}
        model, metadata = await get_llm_for_step(uow, solution_id, PipelineStepEnum.GENERATE_FEEDBACK)

    criteria_for_feedback: list[CriterionInFeedbackDTO] = []
    for check in checks:
        criterion_id = task_criterion_id_to_criterion_id_map[check.task_criterion_id]
        criteria_for_feedback.append(
            CriterionInFeedbackDTO(
                description=criterion_id_to_description_map[criterion_id],
                comment=check.comment,
                is_passed=check.is_passed,
            )
        )

    system_content = prompt_builder.build(prompt_path="feedback/system.tpl")
    user_content = prompt_builder.build(
        prompt_path="feedback/user.tpl", criteria=criteria_for_feedback
    )

    answer = await model.run(system_content, user_content)
    feedback = answer.content
    await artifact_storage.save_artifact(solution_id, PipelineStepEnum.GENERATE_FEEDBACK, feedback)

    metadata.input_tokens = answer.input_tokens
    metadata.output_tokens = answer.output_tokens
    async with uow.connection() as conn, conn.transaction():
        workspace_id = await get_workspace_id(uow, solution_id)
        await charge_for_llm_call(uow, workspace_id, metadata)
        await uow.solutions.update(solution.id, SolutionUpdateDTO(steps=[*solution.steps, PipelineStepEnum.GENERATE_FEEDBACK]))

    return feedback