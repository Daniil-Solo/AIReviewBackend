from dependency_injector.wiring import Provide, inject
from pydantic import TypeAdapter

from src.application.solutions.utils import get_workspace_id
from src.application.transactions.utils import charge_for_llm_call
from src.constants.ai_pipeline import PipelineStepEnum
from src.constants.ai_review import CriterionStageEnum, CriterionCheckStatusEnum
from src.di.container import Container
from src.dto.ai_review.criteria import CriterionCheckDTO, CriterionWithCommentsDTO
from src.dto.solutions.solution_criteria_checks import SolutionCriteriaCheckFiltersDTO, SolutionCriteriaCheckCreateDTO
from src.dto.transactions.metadata import LLMCallTransactionMetadataDTO
from src.infrastructure.ai.llm.interface import LLMInterface
from src.infrastructure.ai.prompt_builder.interface import PromptBuilderInterface
from src.infrastructure.logging import get_logger
from src.infrastructure.sqlalchemy.uow import UnitOfWork
from src.infrastructure.storage.artifact import SolutionArtifactStorage


logger = get_logger()


@inject
async def grade_by_project_doc(
    solution_id: int,
    uow: UnitOfWork = Provide[Container.uow],
    prompt_builder: PromptBuilderInterface = Provide[Container.prompt_builder],
    default_model: LLMInterface = Provide[Container.default_model],
    artifact_storage: SolutionArtifactStorage = Provide[Container.solution_artifact_storage],
) -> None:
    project_doc = await artifact_storage.get_artifact(solution_id, PipelineStepEnum.IMPROVE_DOC)

    criteria = []
    async with uow.connection():
        solution = await uow.solutions.get_by_id(solution_id)
        task_criteria = await uow.task_criteria.get_by_task_id(solution.task_id)

        for task_criterion in task_criteria:
            criterion = await uow.criteria.get_by_id(task_criterion.criterion_id)
            criterion_checks = await uow.solution_criteria_checks.get_list(SolutionCriteriaCheckFiltersDTO(
                task_criterion_id=task_criterion.id,
                solution_id=solution.id,
            ))
            is_checking_stage = criterion.stage != CriterionStageEnum.PROJECT_DOC and criterion.stage is not None
            need_checking_from_other_stage = False
            if is_checking_stage or need_checking_from_other_stage:
                criterion_for_review = CriterionWithCommentsDTO(
                    id=task_criterion.id,
                    description=criterion.description,
                    comments=[check.comment for check in criterion_checks]
                )
                criteria.append(criterion_for_review)

    system_content = prompt_builder.build(
        prompt_path="criteria_checks/projectdoc_grading/system.tpl", criteria=criteria
    )
    user_content = prompt_builder.build(
        prompt_path="criteria_checks/projectdoc_grading/user.tpl", project_doc=project_doc
    )

    answer = await default_model.run(system_content, user_content)
    grading_doc = answer.content
    await artifact_storage.save_artifact(solution_id, PipelineStepEnum.GRADE_BY_PROJECT_DOC, grading_doc)

    metadata = LLMCallTransactionMetadataDTO(
        solution_id=solution_id, task=PipelineStepEnum.GRADE_BY_PROJECT_DOC,
        input_tokens=answer.input_tokens, output_tokens=answer.output_tokens,
    )
    async with uow.connection():
        workspace_id = await get_workspace_id(uow, solution_id)
        await charge_for_llm_call(uow, workspace_id, metadata)

    repaired_json_string = grading_doc.strip().strip("`json")
    criteria_checks = TypeAdapter(list[CriterionCheckDTO]).validate_json(repaired_json_string)

    async with uow.connection():
        for criterion_check in criteria_checks:
            data = SolutionCriteriaCheckCreateDTO(
                task_criterion_id=criterion_check.id,
                solution_id=solution_id,
                comment=criterion_check.comment,
                stage=CriterionStageEnum.PROJECT_DOC,
                status=criterion_check.status,
                is_passed=criterion_check.is_passed
            )
            await uow.solution_criteria_checks.create(data)


@inject
async def grade_by_codebase(
    solution_id: int,
    uow: UnitOfWork = Provide[Container.uow],
    prompt_builder: PromptBuilderInterface = Provide[Container.prompt_builder],
    default_model: LLMInterface = Provide[Container.default_model],
    artifact_storage: SolutionArtifactStorage = Provide[Container.solution_artifact_storage],
) -> None:  # list[CriterionCheckDTO]
    project_tree_doc = await artifact_storage.get_artifact(solution_id, PipelineStepEnum.PREPARE_PROJECT_TREE)
    project_content_doc = await artifact_storage.get_artifact(solution_id, PipelineStepEnum.PREPARE_PROJECT_CONTENT)

    criteria = []
    async with uow.connection():
        solution = await uow.solutions.get_by_id(solution_id)
        task_criteria = await uow.task_criteria.get_by_task_id(solution.task_id)

        for task_criterion in task_criteria:
            criterion = await uow.criteria.get_by_id(task_criterion.criterion_id)
            criterion_checks = await uow.solution_criteria_checks.get_list(SolutionCriteriaCheckFiltersDTO(
                task_criterion_id=task_criterion.id,
                solution_id=solution.id,
            ))
            is_checking_stage = criterion.stage != CriterionStageEnum.CODEBASE and criterion.stage is not None
            need_checking_from_other_stage = False if not criterion_checks else criterion_checks[-1].status == CriterionCheckStatusEnum.NEEDS_CODE
            if is_checking_stage or need_checking_from_other_stage:
                criterion_for_review = CriterionWithCommentsDTO(
                    id=task_criterion.id,
                    description=criterion.description,
                    comments=[check.comment for check in criterion_checks]
                )
                criteria.append(criterion_for_review)

    system_content = prompt_builder.build(prompt_path="criteria_checks/codebase_grading/system.tpl", criteria=criteria)
    user_content = prompt_builder.build(
        prompt_path="criteria_checks/codebase_grading/user.tpl",
        project_tree=project_tree_doc,
        project_content=project_content_doc,
    )

    answer = await default_model.run(system_content, user_content)
    grading_doc = answer.content
    await artifact_storage.save_artifact(solution_id, PipelineStepEnum.GRADE_BY_CODEBASE, grading_doc)

    metadata = LLMCallTransactionMetadataDTO(
        solution_id=solution_id, task=PipelineStepEnum.GRADE_BY_PROJECT_DOC,
        input_tokens=answer.input_tokens, output_tokens=answer.output_tokens,
    )
    async with uow.connection():
        workspace_id = await get_workspace_id(uow, solution_id)
        await charge_for_llm_call(uow, workspace_id, metadata)

    repaired_json_string = grading_doc.strip().strip("`json")
    criteria_checks = TypeAdapter(list[CriterionCheckDTO]).validate_json(repaired_json_string)

    async with uow.connection():
        for criterion_check in criteria_checks:
            data = SolutionCriteriaCheckCreateDTO(
                task_criterion_id=criterion_check.id,
                solution_id=solution_id,
                comment=criterion_check.comment,
                stage=CriterionStageEnum.PROJECT_DOC,
                status=criterion_check.status,
                is_passed=criterion_check.is_passed
            )
            await uow.solution_criteria_checks.create(data)
