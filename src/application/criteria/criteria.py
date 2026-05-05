from dependency_injector.wiring import Provide, inject
from fastapi import UploadFile
from openai._models import TypeAdapter
from pydantic import ValidationError

from src.application.criteria.utils import check_criterion_level_permissions
from src.application.exceptions import ApplicationError
from src.application.workspaces.common import check_member_role
from src.constants.workspaces import WorkspaceMemberRoleEnum
from src.di.container import Container
from src.dto.criteria.criteria import (
    CriterionCreateDTO,
    CriterionFiltersDTO,
    CriterionResponseDTO,
    CriterionUpdateDTO,
)
from src.dto.tasks.task_criteria import TaskCriteriaCreateDTO
from src.dto.users.user import ShortUserDTO
from src.infrastructure.sqlalchemy.uow import UnitOfWork


@inject
async def create(
    data: CriterionCreateDTO,
    user: ShortUserDTO,
    uow: UnitOfWork = Provide[Container.uow],
) -> CriterionResponseDTO:
    async with uow.connection() as conn, conn.transaction():
        await check_criterion_level_permissions(uow, user, data.workspace_id, data.task_id)

        criterion = await uow.criteria.create(data, created_by=user.id)

        if data.task_id is not None:
            task_criteria_data = TaskCriteriaCreateDTO(
                task_id=data.task_id,
                criterion_id=criterion.id,
                weight=1.0,
            )
            await uow.task_criteria.create(task_criteria_data)

        return criterion


@inject
async def get_one(
    criterion_id: int,
    user: ShortUserDTO,
    uow: UnitOfWork = Provide[Container.uow],
) -> CriterionResponseDTO:
    async with uow.connection():
        criterion = await uow.criteria.get_by_id(criterion_id)

        if criterion.workspace_id is not None:
            await check_member_role(uow, user.id, criterion.workspace_id)
        elif criterion.task_id is not None:
            task = await uow.tasks.get_by_id(criterion.task_id)
            await check_member_role(uow, user.id, task.workspace_id)

        return criterion


@inject
async def get_list(
    filters: CriterionFiltersDTO,
    _: ShortUserDTO,
    uow: UnitOfWork = Provide[Container.uow],
) -> list[CriterionResponseDTO]:
    async with uow.connection():
        return await uow.criteria.get_list(filters)


@inject
async def get_list_for_task(
    task_id: int,
    filters: CriterionFiltersDTO,
    user: ShortUserDTO,
    uow: UnitOfWork = Provide[Container.uow],
) -> list[CriterionResponseDTO]:
    async with uow.connection():
        task = await uow.tasks.get_by_id(task_id)
        await check_member_role(
            uow,
            user.id,
            task.workspace_id,
            allowed_roles={WorkspaceMemberRoleEnum.TEACHER, WorkspaceMemberRoleEnum.OWNER},
        )
        filters.task_id = task_id
        filters.workspace_id = task.workspace_id
        return await uow.criteria.get_list(filters)


@inject
async def get_workspace_criteria(
    workspace_id: int,
    filters: CriterionFiltersDTO,
    user: ShortUserDTO,
    uow: UnitOfWork = Provide[Container.uow],
) -> list[CriterionResponseDTO]:
    async with uow.connection():
        await check_member_role(uow, user.id, workspace_id)
        return await uow.criteria.get_workspace_criteria(workspace_id, filters)


@inject
async def update(
    criterion_id: int,
    data: CriterionUpdateDTO,
    user: ShortUserDTO,
    uow: UnitOfWork = Provide[Container.uow],
) -> CriterionResponseDTO:
    async with uow.connection() as conn, conn.transaction():
        criterion = await uow.criteria.get_by_id(criterion_id)
        await check_criterion_level_permissions(uow, user, data.workspace_id, data.task_id)
        return await uow.criteria.update(criterion.id, data)


@inject
async def delete(
    criterion_id: int,
    user: ShortUserDTO,
    uow: UnitOfWork = Provide[Container.uow],
) -> None:
    async with uow.connection() as conn, conn.transaction():
        criterion = await uow.criteria.get_by_id(criterion_id)
        await check_criterion_level_permissions(uow, user, criterion.workspace_id, criterion.task_id)

        await uow.criteria.delete(criterion_id)


@inject
async def get_available_tags(
    _: ShortUserDTO,
    uow: UnitOfWork = Provide[Container.uow],
) -> list[str]:
    async with uow.connection():
        return await uow.criteria.get_available_tags()


@inject
async def import_criteria(
    file: UploadFile,
    workspace_id: int | None,
    task_id: int | None,
    user: ShortUserDTO,
    uow: UnitOfWork = Provide[Container.uow],
) -> list[CriterionResponseDTO]:
    content = await file.read()
    try:
        criteria_list = TypeAdapter(list[CriterionCreateDTO]).validate_json(content.decode("utf-8"))
    except ValidationError as ex:
        raise ApplicationError(message=f"Некорректный формат файла\n{ex}", code="invalid_file_format") from ex

    async with uow.connection() as conn, conn.transaction():
        await check_criterion_level_permissions(uow, user, workspace_id, task_id)

        for criterion_data in criteria_list:
            criterion_data.workspace_id = workspace_id
            criterion_data.task_id = task_id
        created_criteria = await uow.criteria.create_batch(criteria_list, created_by=user.id)

        if task_id is not None:
            for criterion in created_criteria:
                task_criteria_data = TaskCriteriaCreateDTO(
                    task_id=task_id,
                    criterion_id=criterion.id,
                    weight=1.0,
                )
                await uow.task_criteria.create(task_criteria_data)

        return created_criteria
