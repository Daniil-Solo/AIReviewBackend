from dependency_injector.wiring import Provide, inject

from src.application.workspaces.common import check_member_role
from src.constants.workspaces import WorkspaceMemberRoleEnum
from src.di.container import Container
from src.dto.tasks.tasks import TaskCreateDTO, TaskResponseDTO, TaskUpdateDTO
from src.dto.users.user import ShortUserDTO
from src.infrastructure.sqlalchemy.uow import UnitOfWork


@inject
async def create(
    data: TaskCreateDTO,
    user: ShortUserDTO,
    uow: UnitOfWork = Provide[Container.uow],
) -> TaskResponseDTO:
    async with uow.connection():
        await check_member_role(
            uow,
            user.id,
            data.workspace_id,
            allowed_roles={WorkspaceMemberRoleEnum.OWNER, WorkspaceMemberRoleEnum.TEACHER},
        )
        return await uow.tasks.create(data, created_by=user.id)


@inject
async def update(
    task_id: int,
    data: TaskUpdateDTO,
    user: ShortUserDTO,
    uow: UnitOfWork = Provide[Container.uow],
) -> TaskResponseDTO:
    async with uow.connection():
        task = await uow.tasks.get_by_id(task_id)
        await check_member_role(
            uow,
            user.id,
            task.workspace_id,
            allowed_roles={WorkspaceMemberRoleEnum.OWNER, WorkspaceMemberRoleEnum.TEACHER},
        )
        return await uow.tasks.update(task_id, data)


@inject
async def get(
    task_id: int,
    user: ShortUserDTO,
    uow: UnitOfWork = Provide[Container.uow],
) -> TaskResponseDTO:
    async with uow.connection():
        task = await uow.tasks.get_by_id(task_id)
        await check_member_role(
            uow,
            user.id,
            task.workspace_id,
            allowed_roles={WorkspaceMemberRoleEnum.OWNER, WorkspaceMemberRoleEnum.TEACHER},
        )
        return task


@inject
async def get_public(
    task_id: int,
    user: ShortUserDTO,
    uow: UnitOfWork = Provide[Container.uow],
) -> TaskResponseDTO:
    async with uow.connection():
        task = await uow.tasks.get_by_id(task_id)
        await check_member_role(uow, user.id, task.workspace_id)
        return await uow.tasks.get_public_by_id(task_id)


@inject
async def delete(
    task_id: int,
    user: ShortUserDTO,
    uow: UnitOfWork = Provide[Container.uow],
) -> None:
    async with uow.connection():
        task = await uow.tasks.get_by_id(task_id)
        await check_member_role(
            uow,
            user.id,
            task.workspace_id,
            allowed_roles={WorkspaceMemberRoleEnum.OWNER, WorkspaceMemberRoleEnum.TEACHER},
        )
        await uow.tasks.delete(task_id)
