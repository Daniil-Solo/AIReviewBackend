from dependency_injector.wiring import Provide, inject

from src.application.criteria.utils import check_criterion_level_permissions
from src.application.exceptions import ForbiddenError
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
    user: ShortUserDTO,
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

        is_global = criterion.workspace_id is None and criterion.task_id is None

        if is_global:
            if not user.is_admin:
                raise ForbiddenError(
                    message="Удаление глобального критерия доступно только администраторам",
                    code="criterion_access_denied",
                )
        elif criterion.workspace_id is not None:
            await check_member_role(
                uow,
                user.id,
                criterion.workspace_id,
                allowed_roles={WorkspaceMemberRoleEnum.OWNER, WorkspaceMemberRoleEnum.TEACHER},
            )
        elif criterion.task_id is not None:
            task = await uow.tasks.get_by_id(criterion.task_id)
            await check_member_role(
                uow,
                user.id,
                task.workspace_id,
                allowed_roles={WorkspaceMemberRoleEnum.OWNER, WorkspaceMemberRoleEnum.TEACHER},
            )

        await uow.criteria.delete(criterion_id)


@inject
async def get_available_tags(
    user: ShortUserDTO,
    uow: UnitOfWork = Provide[Container.uow],
) -> list[str]:
    async with uow.connection():
        return await uow.criteria.get_available_tags()
