import datetime

from dependency_injector.wiring import Provide, inject

from src.application.exceptions import ApplicationError, ConflictError, EntityNotFoundError
from src.application.workspaces.common import check_member_role
from src.constants.workspaces import WorkspaceMemberRoleEnum
from src.di.container import Container
from src.dto.users.user import ShortUserDTO
from src.dto.workspaces.join import JoinBySlugDTO, JoinResponseDTO
from src.dto.workspaces.member import (
    TransferOwnershipDTO,
    WorkspaceMemberCreateDTO,
    WorkspaceMemberResponseDTO,
    WorkspaceMemberUpdateDTO,
)
from src.dto.workspaces.workspace import WorkspaceResponseDTO
from src.infrastructure.auth.password import verify_password
from src.infrastructure.sqlalchemy.uow import UnitOfWork


@inject
async def join_to_workspace(
    data: JoinBySlugDTO,
    user: ShortUserDTO,
    uow: UnitOfWork = Provide[Container.uow],
) -> JoinResponseDTO:
    async with uow.connection() as conn:
        rule = await uow.workspace_join_rules.get_one(slug=data.slug)

        try:
            await uow.workspace_members.get_by_user_and_workspace(user.id, rule.workspace_id)
            raise ConflictError(message="Пользователь уже является участником пространства", code="already_member")
        except EntityNotFoundError:
            pass

        if not rule.is_active:
            raise ApplicationError(message="Приглашение неактивно", code="joining_inactive")

        if rule.expired_at and rule.expired_at < datetime.datetime.now(datetime.UTC):
            raise ApplicationError(message="Срок действия приглашения истёк", code="joining_expired")

        if rule.hashed_password is not None:
            if not data.password:
                raise ApplicationError(message="Требуется пароль для вступления", code="required_joining_password")
            if not verify_password(data.password, rule.hashed_password):
                raise ApplicationError(message="Неверный пароль для вступления", code="invalid_joining_password")

        async with conn.transaction():
            await uow.workspace_members.create(
                WorkspaceMemberCreateDTO(
                    user_id=user.id,
                    workspace_id=rule.workspace_id,
                    role=rule.role,
                )
            )
            await uow.workspace_join_rules.increment_used_count(rule.id)

        return JoinResponseDTO(workspace_id=rule.workspace_id)


@inject
async def update_member(
    workspace_id: int,
    member_id: int,
    data: WorkspaceMemberUpdateDTO,
    user: ShortUserDTO,
    uow: UnitOfWork = Provide[Container.uow],
) -> WorkspaceMemberResponseDTO:
    async with uow.connection():
        await check_member_role(uow, user.id, workspace_id, allowed_roles={WorkspaceMemberRoleEnum.OWNER})

        target_member = await uow.workspace_members.get_by_id(member_id)
        if target_member.workspace_id != workspace_id:
            raise EntityNotFoundError(message="Участник не найден в пространстве")

        if target_member.role == WorkspaceMemberRoleEnum.OWNER:
            raise ApplicationError(
                message="Нельзя изменить роль у владельца пространства", code="cannot_change_owner_role"
            )

        if data.role == WorkspaceMemberRoleEnum.OWNER:
            raise ApplicationError(message="Нельзя назначить участнику роль Владелец", code="owner_not_available")

        return await uow.workspace_members.update(member_id, data)


@inject
async def leave_workspace(
    workspace_id: int,
    user: ShortUserDTO,
    uow: UnitOfWork = Provide[Container.uow],
) -> None:
    async with uow.connection():
        member = await uow.workspace_members.get_by_user_and_workspace(user.id, workspace_id)

        if member.role == WorkspaceMemberRoleEnum.OWNER:
            raise ApplicationError(
                message="Участник с ролью Владелец не может покинуть пространство", code="owner_cannot_leave"
            )

        await uow.workspace_members.delete(member.id)


@inject
async def change_workspace_owner(
    workspace_id: int,
    data: TransferOwnershipDTO,
    user: ShortUserDTO,
    uow: UnitOfWork = Provide[Container.uow],
) -> WorkspaceResponseDTO:
    async with uow.connection() as conn:
        current_owner = await check_member_role(
            uow, user.id, workspace_id, allowed_roles={WorkspaceMemberRoleEnum.OWNER}
        )
        new_owner = await uow.workspace_members.get_by_id(data.member_id)
        if new_owner.workspace_id != workspace_id:
            raise EntityNotFoundError(message="Участник не найден в этом пространстве")

        if new_owner.id == current_owner.id:
            raise ConflictError(message="Передача прав сама себе невозможна", code="self_transfer_disabled")

        async with conn.transaction():
            await uow.workspace_members.update(
                new_owner.id, WorkspaceMemberUpdateDTO(role=WorkspaceMemberRoleEnum.OWNER)
            )
            await uow.workspace_members.update(
                current_owner.id, WorkspaceMemberUpdateDTO(role=WorkspaceMemberRoleEnum.TEACHER)
            )

        return await uow.workspaces.get_by_id(workspace_id)


@inject
async def delete_member(
    workspace_id: int,
    member_id: int,
    user: ShortUserDTO,
    uow: UnitOfWork = Provide[Container.uow],
) -> None:
    async with uow.connection():
        await check_member_role(
            uow, user.id, workspace_id, allowed_roles={WorkspaceMemberRoleEnum.OWNER, WorkspaceMemberRoleEnum.TEACHER}
        )

        target_member = await uow.workspace_members.get_by_id(member_id)
        if target_member.workspace_id != workspace_id:
            raise EntityNotFoundError(message="Участник не найден в пространстве")

        if target_member.role == WorkspaceMemberRoleEnum.OWNER:
            raise ApplicationError(message="Нельзя удалить владельца пространства", code="cannot_delete_owner")

        if target_member.user_id == user.id:
            raise ApplicationError(message="Нельзя удалить самого себя", code="cannot_delete_self")

        await uow.workspace_members.delete(member_id)
