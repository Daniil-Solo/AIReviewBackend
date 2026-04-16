import re

from botocore.exceptions import ClientError
from dependency_injector.wiring import Provide, inject
from fastapi import UploadFile
import httpx

from src.application.exceptions import ApplicationError, EntityNotFoundError, ForbiddenError
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
    SolutionShortResponseDTO,
    SolutionUpdateDTO,
)
from src.dto.users.user import ShortUserDTO
from src.dto.workspaces.member import WorkspaceMemberFiltersDTO
from src.infrastructure.sqlalchemy.uow import UnitOfWork
from src.infrastructure.storage.artifact import SolutionArtifactStorage
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

        workspace = await uow.workspaces.get_by_id(task.workspace_id)
        owner_member = (await uow.workspace_members.get_list(WorkspaceMemberFiltersDTO(workspace_id=workspace.id, roles=[WorkspaceMemberRoleEnum.OWNER])))[0]
        balance = await uow.transactions.get_balance_by_user_id(owner_member.user_id)
        initial_status = SolutionStatusEnum.ERROR if balance < 0 else  SolutionStatusEnum.AI_REVIEW

        solution = await uow.solutions.create(SolutionCreateDTO(**data.model_dump(), link=link), user.id)
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
    async with uow.connection():
        solution = await uow.solutions.get_by_id(solution_id)
        if solution.created_by != user.id:
            raise ForbiddenError(message="Только автор решения может отменить его")
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
