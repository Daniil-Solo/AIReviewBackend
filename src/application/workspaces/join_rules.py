from dependency_injector.wiring import Provide, inject

from src.application.exceptions import ApplicationError
from src.application.workspaces.common import check_member_role
from src.constants.workspaces import WorkspaceMemberRoleEnum
from src.di.container import Container
from src.dto.users.user import ShortUserDTO
from src.dto.workspaces.join import SlugCheckResponseDTO
from src.dto.workspaces.join_rule import (
    WorkspaceJoinRuleCreateDTO,
    WorkspaceJoinRuleRequestCreateDTO,
    WorkspaceJoinRuleRequestUpdateDTO,
    WorkspaceJoinRuleResponseDTO,
    WorkspaceJoinRuleUpdateDTO,
)
from src.infrastructure.auth.password import hash_password
from src.infrastructure.sqlalchemy.uow import UnitOfWork


@inject
async def check_slug_available(
    slug: str,
    uow: UnitOfWork = Provide[Container.uow],
) -> SlugCheckResponseDTO:
    async with uow.connection():
        exists = await uow.workspace_join_rules.exists_by_slug(slug)
        return SlugCheckResponseDTO(slug=slug, is_available=not exists)


@inject
async def create_join_rule(
    workspace_id: int,
    data: WorkspaceJoinRuleRequestCreateDTO,
    user: ShortUserDTO,
    uow: UnitOfWork = Provide[Container.uow],
) -> WorkspaceJoinRuleResponseDTO:
    async with uow.connection():
        await check_member_role(
            uow, user.id, workspace_id, allowed_roles={WorkspaceMemberRoleEnum.OWNER, WorkspaceMemberRoleEnum.TEACHER}
        )

        if data.role == WorkspaceMemberRoleEnum.OWNER:
            raise ApplicationError(
                message="Создание приглашение с ролью Владелец невозможно", code="not_available__join_rule_role"
            )

        hashed_password = hash_password(data.password) if data.password else None
        data = WorkspaceJoinRuleCreateDTO(**data.model_dump(), hashed_password=hashed_password)
        return await uow.workspace_join_rules.create(data)


@inject
async def update_join_rule(
    workspace_id: int,
    rule_id: int,
    data: WorkspaceJoinRuleRequestUpdateDTO,
    user: ShortUserDTO,
    uow: UnitOfWork = Provide[Container.uow],
) -> WorkspaceJoinRuleResponseDTO:
    async with uow.connection():
        await check_member_role(
            uow, user.id, workspace_id, allowed_roles={WorkspaceMemberRoleEnum.OWNER, WorkspaceMemberRoleEnum.TEACHER}
        )

        if data.role == WorkspaceMemberRoleEnum.OWNER:
            raise ApplicationError(
                message="Роль Владелец недопустима для приглашения", code="not_available__join_rule_role"
            )

        hashed_password = hash_password(data.password) if data.password else None
        data = WorkspaceJoinRuleUpdateDTO(**data.model_dump(), hashed_password=hashed_password)
        return await uow.workspace_join_rules.update(rule_id, data)


@inject
async def delete_join_rule(
    workspace_id: int,
    rule_id: int,
    user: ShortUserDTO,
    uow: UnitOfWork = Provide[Container.uow],
) -> None:
    async with uow.connection():
        await check_member_role(
            uow, user.id, workspace_id, allowed_roles={WorkspaceMemberRoleEnum.OWNER, WorkspaceMemberRoleEnum.TEACHER}
        )
        await uow.workspace_join_rules.delete(rule_id)
