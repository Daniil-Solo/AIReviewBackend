import io
import re
from typing import IO, Any

from botocore.exceptions import ClientError
from dependency_injector.wiring import Provide, inject
from fastapi import UploadFile
import httpx

from src.application.exceptions import ApplicationError, EntityNotFoundError
from src.application.solutions.common import check_solution_permissions
from src.application.workspaces.common import check_member_role
from src.constants.ai_pipeline import ALL_STEPS, PipelineStepEnum
from src.constants.ai_review import SolutionFormatEnum, SolutionStatusEnum
from src.constants.workspaces import WorkspaceMemberRoleEnum
from src.di.container import Container
from src.dto.solutions.solutions import (
    SolutionCreateDTO,
    SolutionCreateRequestDTO,
    SolutionFiltersDTO,
    SolutionFiltersRequestDTO,
    SolutionFinalReviewDTO,
    SolutionShortResponseDTO,
    SolutionUpdateDTO,
)
from src.dto.users.user import ShortUserDTO
from src.dto.workspaces.member import WorkspaceMemberFiltersDTO
from src.infrastructure.solution_artifact_storage.interface import SolutionArtifactStorage
from src.infrastructure.solution_storage.interface import SolutionStorage
from src.infrastructure.sqlalchemy.uow import UnitOfWork
from src.settings import settings


async def get_repo_zip(github_repo_link: str, github_repo_branch: str) -> IO[Any]:
    url = github_repo_link.strip().rstrip("/")

    match = re.search(r"github\.com/([^/]+)/([^/]+)/?$", url, re.IGNORECASE)
    if not match:
        raise ApplicationError(message="Cсылка невалидная", code="github_link_invalid")

    zip_url = url.replace("github.com", "codeload.github.com") + f"/zip/refs/heads/{github_repo_branch}"

    async with httpx.AsyncClient() as client:
        response = await client.get(zip_url)
        if response.status_code == 200:
            return io.BytesIO(response.content)
        if response.status_code == 404:
            raise ApplicationError(message="Репозиторий не найден", code="github_repo_not_found")
        raise ApplicationError(
            message="Возникла непредвиденная ошибка обращения к GitHub", code="github_unexpected_error"
        )


@inject
async def create(
    data: SolutionCreateRequestDTO,
    file: UploadFile | None,
    user: ShortUserDTO,
    uow: UnitOfWork = Provide[Container.uow],
    solution_storage: SolutionStorage = Provide[Container.solution_storage],
) -> SolutionShortResponseDTO:
    if data.format == SolutionFormatEnum.GITHUB:
        if data.github_repo_branch is None or data.github_repo_link is None:
            raise ApplicationError(
                message="Не указана ссылка или ветка на GitHub", code="repo_link_branch_not_received"
            )
        file_content = await get_repo_zip(data.github_repo_link, data.github_repo_branch)
        filename = "solution.zip"
    elif data.format == SolutionFormatEnum.ZIP:
        if file is None:
            raise ApplicationError(message="Файл обязателен для ZIP формата", code="zip_file_not_received")
        file_content = file.file
        filename = file.filename or "solution.zip"
    else:
        raise ApplicationError(message=f"Неожиданный формат решения: {data.format}", code="unexpected_format")

    artifact_path = await solution_storage.upload_solution(
        file_content,
        filename,
        data.task_id,
        user.id,
    )

    async with uow.connection() as conn, conn.transaction():
        task = await uow.tasks.get_by_id(data.task_id)
        await check_member_role(uow, user.id, task.workspace_id)

        existing_solutions = await uow.solutions.get_list(SolutionFiltersDTO(task_id=data.task_id, created_by=user.id))
        if len(existing_solutions) >= settings.solutions.MAX_UPLOADS_PER_TASK:
            raise ApplicationError(
                message=f"Превышен лимит загрузок решений ({settings.solutions.MAX_UPLOADS_PER_TASK}) для этой задачи",
                code="solution_upload_limit_exceeded",
            )

        workspace = await uow.workspaces.get_by_id(task.workspace_id)
        owner_member = (
            await uow.workspace_members.get_list(
                WorkspaceMemberFiltersDTO(workspace_id=workspace.id, roles=[WorkspaceMemberRoleEnum.OWNER])
            )
        )[0]
        balance = await uow.transactions.get_balance_by_user_id(owner_member.user_id)
        initial_status = SolutionStatusEnum.ERROR if balance < 0 else SolutionStatusEnum.PROJECT_GENERATION

        solution = await uow.solutions.create(
            SolutionCreateDTO(**data.model_dump(), artifact_path=artifact_path), user.id
        )
        solution = await uow.solutions.update(
            solution.id,
            SolutionUpdateDTO(status=initial_status, steps=[]),
        )
        if balance > 0:
            await uow.pipeline_tasks.create_many(solution.id, ALL_STEPS)
    return SolutionShortResponseDTO.model_validate(solution)


@inject
async def get(
    solution_id: int,
    user: ShortUserDTO,
    uow: UnitOfWork = Provide[Container.uow],
) -> SolutionShortResponseDTO:
    async with uow.connection():
        solution = await check_solution_permissions(uow, user.id, solution_id)
        author = await uow.users.get_by_id(solution.created_by)
        sol_dict = solution.model_dump()
        sol_dict["author"] = author.as_short()
        return SolutionShortResponseDTO(**sol_dict)


@inject
async def cancel(
    solution_id: int,
    user: ShortUserDTO,
    uow: UnitOfWork = Provide[Container.uow],
) -> None:
    async with uow.connection() as conn, conn.transaction():
        solution = await uow.solutions.get_by_id(solution_id)
        await check_solution_permissions(uow, user.id, solution.id)

        if solution.status not in (
            SolutionStatusEnum.PROJECT_GENERATION,
            SolutionStatusEnum.VALIDATION_WAITING,
            SolutionStatusEnum.CRITERIA_GRADING,
        ):
            raise ApplicationError(
                message="Отмена проверки решения возможна только во время AI-проверки", code="solution_status_invalid"
            )

        await uow.pipeline_tasks.delete_many_not_completed(solution_id)
        await uow.solutions.update(solution_id, SolutionUpdateDTO(status=SolutionStatusEnum.CANCELLED))


@inject
async def get_list_by_task(
    task_id: int,
    user: ShortUserDTO,
    uow: UnitOfWork = Provide[Container.uow],
) -> list[SolutionShortResponseDTO]:
    async with uow.connection():
        task = await uow.tasks.get_by_id(task_id)
        workspace = await uow.workspaces.get_by_id(task.workspace_id)
        await check_member_role(
            uow, user.id, workspace.id, {WorkspaceMemberRoleEnum.OWNER, WorkspaceMemberRoleEnum.TEACHER}
        )
        filters = SolutionFiltersDTO(task_id=task_id)
        solutions = await uow.solutions.get_list(filters)

        user_ids = list({s.created_by for s in solutions})
        users = {u.id: u.as_short() for u in await uow.users.get_by_ids(user_ids)}

        result = []
        for solution in solutions:
            sol_dict = solution.model_dump()
            sol_dict["author"] = users.get(solution.created_by)
            result.append(SolutionShortResponseDTO(**sol_dict))

        return result


@inject
async def get_my_solutions(
    filters: SolutionFiltersRequestDTO,
    user: ShortUserDTO,
    uow: UnitOfWork = Provide[Container.uow],
) -> list[SolutionShortResponseDTO]:
    async with uow.connection():
        dao_filters = SolutionFiltersDTO(created_by=user.id, task_id=filters.task_id)
        return await uow.solutions.get_list(dao_filters)


@inject
async def get_artifact(
    solution_id: int,
    step: PipelineStepEnum,
    user: ShortUserDTO,
    uow: UnitOfWork = Provide[Container.uow],
    artifact_storage: SolutionArtifactStorage = Provide[Container.solution_artifact_storage],
) -> str:
    async with uow.connection():
        await check_solution_permissions(uow, user.id, solution_id)
        try:
            return await artifact_storage.get_artifact(solution_id, str(step))
        except ClientError as e:
            error_code = e.response.get("Error", {}).get("Code", "")
            if error_code == "NoSuchKey":
                raise EntityNotFoundError(message="Артефакт не найден") from e
            raise


@inject
async def final_review(
    solution_id: int,
    data: SolutionFinalReviewDTO,
    user: ShortUserDTO,
    uow: UnitOfWork = Provide[Container.uow],
) -> SolutionShortResponseDTO:
    async with uow.connection() as conn, conn.transaction():
        solution = await uow.solutions.get_by_id(solution_id)

        if solution.status not in (SolutionStatusEnum.HUMAN_REVIEW, SolutionStatusEnum.REVIEWED):
            raise ApplicationError(
                message="Вынесение финального вердикта в этом статусе невозможно",
                code="solution_status_invalid",
            )

        await check_solution_permissions(uow, user.id, solution.id, allow_author=False)

        updated_solution = await uow.solutions.update(
            solution_id,
            SolutionUpdateDTO(
                status=SolutionStatusEnum.REVIEWED,
                human_grade=data.human_grade,
                human_feedback=data.human_feedback,
                ai_feedback=data.ai_feedback,
            ),
        )

        return SolutionShortResponseDTO.model_validate(updated_solution)


@inject
async def update_label(
    solution_id: int,
    label: str,
    user: ShortUserDTO,
    uow: UnitOfWork = Provide[Container.uow],
) -> SolutionShortResponseDTO:
    async with uow.connection():
        await check_solution_permissions(uow, user.id, solution_id, allow_author=True)
        updated_solution = await uow.solutions.update(solution_id, SolutionUpdateDTO(label=label))
        return SolutionShortResponseDTO.model_validate(updated_solution)


@inject
async def approve_project_doc(
    solution_id: int,
    file: UploadFile,
    user: ShortUserDTO,
    uow: UnitOfWork = Provide[Container.uow],
    artifact_storage: SolutionArtifactStorage = Provide[Container.solution_artifact_storage],
) -> SolutionShortResponseDTO:
    async with uow.connection() as conn, conn.transaction():
        solution = await uow.solutions.get_by_id(solution_id)
        await check_solution_permissions(uow, user.id, solution.id, allow_author=True)

        if solution.status != SolutionStatusEnum.VALIDATION_WAITING:
            raise ApplicationError(
                message="Подтверждение ProjectDoc возможно только в статусе VALIDATION_WAITING",
                code="solution_status_invalid",
            )

        content = await file.read()
        text_content = content.decode("utf-8")

        await artifact_storage.save_artifact(
            solution_id,
            PipelineStepEnum.VALIDATE_PROJECT_DOC,
            text_content,
        )

        new_steps = [*solution.steps, PipelineStepEnum.VALIDATE_PROJECT_DOC]

        updated_solution = await uow.solutions.update(
            solution_id,
            SolutionUpdateDTO(
                status=SolutionStatusEnum.CRITERIA_GRADING,
                steps=new_steps,
            ),
        )

        return SolutionShortResponseDTO.model_validate(updated_solution)
