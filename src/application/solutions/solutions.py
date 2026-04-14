import re

from dependency_injector.wiring import Provide, inject
from fastapi import UploadFile
import httpx

from src.application.exceptions import ApplicationError, ForbiddenError
from src.application.workspaces.common import check_member_role
from src.constants.ai_pipeline import ALL_STEPS
from src.constants.ai_review import SolutionFormatEnum, SolutionStatusEnum
from src.constants.workspaces import WorkspaceMemberRoleEnum
from src.di.container import Container
from src.dto.solutions.solutions import (
    SolutionCreateDTO,
    SolutionCreateRequestDTO,
    SolutionShortResponseDTO,
    SolutionUpdateDTO,
)
from src.dto.users.user import ShortUserDTO
from src.infrastructure.sqlalchemy.uow import UnitOfWork
from src.infrastructure.storage.interface import SolutionStorage


async def validate_github_link(link: str) -> None:
    url = link.strip().rstrip("/")

    match = re.search(r"github\.com/([^/]+)/([^/]+)/?$", url, re.IGNORECASE)
    if match:
        owner, repo = match.group(1), match.group(2)
    else:
        raise ApplicationError(message="Cсылка невалидная", code="github_link_invalid")

    api_url = f"https://api.github.com/repos/{owner}/{repo}"

    async with httpx.AsyncClient() as client:
        response = await client.get(api_url)

        if response.status_code == 200:
            return
        if response.status_code == 404:
            raise ApplicationError(message="Репозиторий не найден", code="github_repo_not_found")
        raise ApplicationError(
            message="Возникла непредвиденная ошибка обращения к GitHub", code="github_unexpected_error"
        )


@inject
async def create(
    data: SolutionCreateRequestDTO,
    file: UploadFile | None,
    link: str | None,
    user: ShortUserDTO,
    uow: UnitOfWork = Provide[Container.uow],
    solution_storage: SolutionStorage = Provide[Container.solution_storage],
) -> SolutionShortResponseDTO:
    if data.format == SolutionFormatEnum.ZIP:
        if file is None:
            raise ApplicationError(message="Файл обязателен для ZIP формата", code="zip_file_not_received")
        link = await solution_storage.upload_solution(
            file.file,
            file.filename or "solution.zip",
            data.task_id,
            user.id,
        )
    elif data.format == SolutionFormatEnum.GITHUB:
        if link is None:
            raise ApplicationError(message="Не передана ссылка на github", code="github_link_not_received")

        await validate_github_link(link)

    async with uow.connection() as conn, conn.transaction():
        task = await uow.tasks.get_by_id(data.task_id)
        await check_member_role(uow, user.id, task.workspace_id)
        solution = await uow.solutions.create(SolutionCreateDTO(**data.model_dump(), link=link), user.id)
        solution = await uow.solutions.update(
            solution.id,
            SolutionUpdateDTO(status=SolutionStatusEnum.AI_REVIEW, steps=[]),
        )
        await uow.pipeline_tasks.create_tasks(solution.id, ALL_STEPS)
    return SolutionShortResponseDTO.model_validate(solution)


@inject
async def get(
    solution_id: int,
    user: ShortUserDTO,
    uow: UnitOfWork = Provide[Container.uow],
) -> SolutionShortResponseDTO:
    async with uow.connection():
        solution = await uow.solutions.get_by_id(solution_id)
        task = await uow.tasks.get_by_id(solution.task_id)
        member = await check_member_role(uow, user.id, task.workspace_id)
        if solution.created_by != user.id and member.role not in {
            WorkspaceMemberRoleEnum.OWNER,
            WorkspaceMemberRoleEnum.TEACHER,
        }:
            raise ForbiddenError(message="Пользователь не имеет доступ к этому решению")
        return SolutionShortResponseDTO.model_validate(solution)


@inject
async def cancel(
    solution_id: int,
    user: ShortUserDTO,
    uow: UnitOfWork = Provide[Container.uow],
) -> None:
    async with uow.connection():
        solution = await uow.solutions.get_by_id(solution_id)
        if solution.created_by != user.id:
            raise ForbiddenError(message="Нет доступа к этому решению")
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
        return await uow.solutions.get_list_by_task(task_id)
