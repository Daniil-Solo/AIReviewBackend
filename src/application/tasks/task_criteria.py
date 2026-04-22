from dependency_injector.wiring import Provide, inject

from src.application.workspaces.common import check_member_role
from src.constants.workspaces import WorkspaceMemberRoleEnum
from src.di.container import Container
from src.dto.tasks.task_criteria import (
    TaskCriteriaCreateBatchDTO,
    TaskCriteriaCreateDTO,
    TaskCriteriaFullResponseDTO,
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
async def create_batch(
    task_id: int,
    data: TaskCriteriaCreateBatchDTO,
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
        for criterion_id in data.criterion_ids:
            data = TaskCriteriaCreateDTO(task_id=task_id, criterion_id=criterion_id, weight=1)
            await uow.task_criteria.create(data)


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
) -> list[TaskCriteriaFullResponseDTO]:
    async with uow.connection():
        task = await uow.tasks.get_by_id(task_id)
        await check_member_role(
            uow,
            user.id,
            task.workspace_id,
            allowed_roles={WorkspaceMemberRoleEnum.OWNER, WorkspaceMemberRoleEnum.TEACHER},
        )
        result = []
        task_criteria = await uow.task_criteria.get_by_task_id(task_id)
        for tc in task_criteria:
            criterion = await uow.criteria.get_by_id(tc.criterion_id)
            result.append(TaskCriteriaFullResponseDTO(**tc.model_dump(), criterion=criterion))
        return result
