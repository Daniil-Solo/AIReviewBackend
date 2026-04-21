from dependency_injector.wiring import Provide, inject
from pydantic import TypeAdapter

from src.application.solutions.utils import get_workspace_id
from src.application.transactions.utils import charge_for_llm_call
from src.constants.ai_pipeline import PipelineStepEnum
from src.di.container import Container
from src.dto.ai_review.criteria import CriterionCheckDTO, CriterionWithCommentsDTO
from src.dto.solutions.solution_criteria_checks import SolutionCriteriaCheckFiltersDTO
from src.dto.tasks.task_criteria import TaskCriteriaFullResponseDTO
from src.dto.transactions.metadata import LLMCallTransactionMetadataDTO
from src.infrastructure.ai.llm.interface import LLMInterface
from src.infrastructure.ai.prompt_builder.interface import PromptBuilderInterface
from src.infrastructure.logging import get_logger
from src.infrastructure.sqlalchemy.uow import UnitOfWork
from src.infrastructure.storage.artifact import SolutionArtifactStorage
from src.settings import ROOT_DIR


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
            criteria.append(criterion)
            criterion_checks = await uow.solution_criteria_checks.get_list(SolutionCriteriaCheckFiltersDTO(
                task_criterion_id=task_criterion.id,
                solution_id=solution.id
            ))
            CriterionWithCommentsDTO(
                id=criterion.id,
                description=criterion.description,
                comments=[check.comment for check in criterion_checks]
            )


    system_content = prompt_builder.build(
        prompt_path="criteria_checks/projectdoc_grading/system.tpl", criteria=criteria
    )
    user_content = prompt_builder.build(
        prompt_path="criteria_checks/projectdoc_grading/user.tpl", project_doc=project_doc
    )

    answer = await default_model.run(system_content, user_content)
    resolve_doc = answer.content
    await artifact_storage.save_artifact(solution_id, PipelineStepEnum.GRADE_BY_PROJECT_DOC, resolve_doc)

    metadata = LLMCallTransactionMetadataDTO(
        solution_id=solution_id, task=PipelineStepEnum.GRADE_BY_PROJECT_DOC,
        input_tokens=answer.input_tokens, output_tokens=answer.output_tokens,
    )
    async with uow.connection():
        workspace_id = await get_workspace_id(uow, solution_id)
        await charge_for_llm_call(uow, workspace_id, metadata)



    # add saving criteria checks

    if answer.content is not None:
        criteria_checks = TypeAdapter(list[CriterionCheckDTO]).validate_json(answer.content)
        logger.info("criteria_checks", criteria_checks=criteria_checks)



@inject
async def grade_by_codebase(
    prompt_builder: PromptBuilderInterface = Provide[Container.prompt_builder],
    default_model: LLMInterface = Provide[Container.default_model],
) -> None:  # list[CriterionCheckDTO]
    criteria = [
        CriterionWithCommentsDTO(
            id=66,
            description="""Для проекта должен быть написан docker-compose.yaml, которого достаточно для запуска всей системы""",
            comments=[
                "В структуре проекта и описании зависимостей отсутствует упоминание файла docker-compose.yaml. Также не указано, что проект упакован в Docker-контейнеры или может быть запущен через Docker. Архитектура предполагает запуск скриптов локально (main.py), без контейнеризации. Вероятно, файл docker-compose.yaml отсутствует. Для проверки требуется анализ корневой директории проекта.",
            ],
        ),
    ]
    with open(ROOT_DIR / "examples" / "project_docs" / "avito-price-prediction" / "project_content.md") as f:
        project_content_doc = f.read()

    with open(ROOT_DIR / "examples" / "project_docs" / "avito-price-prediction" / "project_tree.md") as f:
        project_tree_doc = f.read()

    system_content = prompt_builder.build(prompt_path="criteria_checks/codebase_grading/system.tpl", criteria=criteria)
    user_content = prompt_builder.build(
        prompt_path="criteria_checks/codebase_grading/user.tpl",
        project_tree=project_tree_doc,
        project_content=project_content_doc,
    )

    answer = await default_model.run(system_content, user_content)
    with open("grade_by_codebase.txt", "w") as f:
        f.write(answer.content)

    if answer.content is not None:
        criteria_checks = TypeAdapter(list[CriterionCheckDTO]).validate_json(answer.content)
        logger.info("criteria_checks", criteria_checks=criteria_checks)
