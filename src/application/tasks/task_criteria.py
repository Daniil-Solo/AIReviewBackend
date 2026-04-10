from dependency_injector.wiring import Provide, inject

from src.application.workspaces.common import check_member_role
from src.constants.workspaces import WorkspaceMemberRoleEnum
from src.di.container import Container
from src.dto.tasks.task_criteria import (
    TaskCriteriaCreateDTO,
    TaskCriteriaResponseDTO,
    TaskCriteriaUpdateWeightDTO,
)
from src.dto.users.user import ShortUserDTO
from src.infrastructure.sqlalchemy.uow import UnitOfWork


@inject
async def create(
    data: TaskCriteriaCreateDTO,
    user: ShortUserDTO,
    uow: UnitOfWork = Provide[Container.uow],
) -> TaskCriteriaResponseDTO:
    async with uow.connection():
        task = await uow.tasks.get_by_id(data.task_id)
        await check_member_role(
            uow,
            user.id,
            task.workspace_id,
            allowed_roles={WorkspaceMemberRoleEnum.OWNER, WorkspaceMemberRoleEnum.TEACHER},
        )
        return await uow.task_criteria.create(data)


@inject
async def update(
    task_criterion_id: int,
    data: TaskCriteriaUpdateWeightDTO,
    user: ShortUserDTO,
    uow: UnitOfWork = Provide[Container.uow],
) -> TaskCriteriaResponseDTO:
    async with uow.connection():
        task_criterion = await uow.task_criteria.get_by_id(task_criterion_id)
        task = await uow.tasks.get_by_id(task_criterion.task_id)
        await check_member_role(
            uow,
            user.id,
            task.workspace_id,
            allowed_roles={WorkspaceMemberRoleEnum.OWNER, WorkspaceMemberRoleEnum.TEACHER},
        )
        return await uow.task_criteria.update(task_criterion_id, data)


@inject
async def delete(
    task_criterion_id: int,
    user: ShortUserDTO,
    uow: UnitOfWork = Provide[Container.uow],
) -> None:
    async with uow.connection():
        task_criterion = await uow.task_criteria.get_by_id(task_criterion_id)
        task = await uow.tasks.get_by_id(task_criterion.task_id)
        await check_member_role(
            uow,
            user.id,
            task.workspace_id,
            allowed_roles={WorkspaceMemberRoleEnum.OWNER, WorkspaceMemberRoleEnum.TEACHER},
        )
        await uow.task_criteria.delete(task_criterion_id)


@inject
async def get_by_task(
    task_id: int,
    user: ShortUserDTO,
    uow: UnitOfWork = Provide[Container.uow],
) -> list[TaskCriteriaResponseDTO]:
    async with uow.connection():
        task = await uow.tasks.get_by_id(task_id)
        await check_member_role(
            uow,
            user.id,
            task.workspace_id,
            allowed_roles={WorkspaceMemberRoleEnum.OWNER, WorkspaceMemberRoleEnum.TEACHER},
        )
        return await uow.task_criteria.get_by_task_id(task_id)
