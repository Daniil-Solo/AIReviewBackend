from dependency_injector.wiring import Provide, inject

from src.application.workspaces.common import check_member_role
from src.constants.workspaces import WorkspaceMemberRoleEnum
from src.di.container import Container
from src.dto.users.user import ShortUserDTO
from src.dto.workspaces.join_rule import (
    WorkspaceJoinRuleResponseDTO,
)
from src.dto.workspaces.member import WorkspaceMemberCreateDTO, WorkspaceMemberFiltersDTO, WorkspaceMemberResponseDTO
from src.dto.workspaces.workspace import WorkspaceCreateDTO, WorkspaceResponseDTO, WorkspaceUpdateDTO
from src.infrastructure.sqlalchemy.uow import UnitOfWork


@inject
async def create_workspace(
    data: WorkspaceCreateDTO,
    user: ShortUserDTO,
    uow: UnitOfWork = Provide[Container.uow],
) -> WorkspaceResponseDTO:
    async with uow.connection() as conn, conn.transaction():
        workspace = await uow.workspaces.create(data)
        await uow.workspace_members.create(
            WorkspaceMemberCreateDTO(
                user_id=user.id,
                workspace_id=workspace.id,
                role=WorkspaceMemberRoleEnum.OWNER,
            )
        )
        return workspace


@inject
async def update_workspace(
    workspace_id: int,
    data: WorkspaceUpdateDTO,
    user: ShortUserDTO,
    uow: UnitOfWork = Provide[Container.uow],
) -> WorkspaceResponseDTO:
    async with uow.connection():
        await check_member_role(
            uow, user.id, workspace_id, allowed_roles={WorkspaceMemberRoleEnum.OWNER, WorkspaceMemberRoleEnum.TEACHER}
        )
        return await uow.workspaces.update(workspace_id, data)


@inject
async def archive_workspace(
    workspace_id: int,
    user: ShortUserDTO,
    uow: UnitOfWork = Provide[Container.uow],
) -> None:
    async with uow.connection():
        await check_member_role(uow, user.id, workspace_id, allowed_roles={WorkspaceMemberRoleEnum.OWNER})
        await uow.workspaces.archive(workspace_id)


@inject
async def get_workspace(
    workspace_id: int,
    user: ShortUserDTO,
    uow: UnitOfWork = Provide[Container.uow],
) -> WorkspaceResponseDTO:
    async with uow.connection():
        await check_member_role(uow, user.id, workspace_id)
        return await uow.workspaces.get_by_id(workspace_id)


@inject
async def get_workspace_tasks(
    workspace_id: int,
    user: ShortUserDTO,
    uow: UnitOfWork = Provide[Container.uow],
) -> list[dict]:
    async with uow.connection():
        await check_member_role(uow, user.id, workspace_id)
        return []


@inject
async def get_workspace_members(
    workspace_id: int,
    user: ShortUserDTO,
    uow: UnitOfWork = Provide[Container.uow],
) -> list[WorkspaceMemberResponseDTO]:
    async with uow.connection():
        await check_member_role(uow, user.id, workspace_id)
        return await uow.workspace_members.get_list(WorkspaceMemberFiltersDTO(workspace_id=workspace_id))


@inject
async def get_workspace_join_rules(
    workspace_id: int,
    user: ShortUserDTO,
    uow: UnitOfWork = Provide[Container.uow],
) -> list[WorkspaceJoinRuleResponseDTO]:
    async with uow.connection():
        await check_member_role(
            uow, user.id, workspace_id, allowed_roles={WorkspaceMemberRoleEnum.OWNER, WorkspaceMemberRoleEnum.TEACHER}
        )
        return await uow.workspace_join_rules.get_list(workspace_id)
