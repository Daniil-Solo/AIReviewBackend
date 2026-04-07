from fastapi import status
from httpx import AsyncClient, Response
import pytest_asyncio

from src.constants.workspaces import WorkspaceMemberRoleEnum
from src.dto.workspaces.member import TransferOwnershipDTO, WorkspaceMemberFiltersDTO
from src.dto.workspaces.workspace import WorkspaceResponseDTO
from src.infrastructure.auth import create_access_token
from tests.helpers.users import create_users
from tests.helpers.workspaces import create_workspace, add_user_to_workspace


@pytest_asyncio.fixture()
def request_transfer_ownership(client: AsyncClient):
    async def inner(workspace_id: int, data: TransferOwnershipDTO, token: str) -> Response:
        return await client.patch(
            f"/api/v1/workspaces/{workspace_id}/owner",
            json=data.model_dump(by_alias=True),
            headers={"Authorization": f"Bearer {token}"},
        )

    return inner


@pytest_asyncio.fixture()
def transfer_ownership(request_transfer_ownership):
    async def inner(workspace_id: int, data: TransferOwnershipDTO, token: str) -> WorkspaceResponseDTO:
        response = await request_transfer_ownership(workspace_id, data, token)
        assert response.status_code == status.HTTP_200_OK
        return WorkspaceResponseDTO.model_validate_json(response.text)

    return inner


async def test__success(uow, transfer_ownership):
    owner = (await create_users(uow))[0]
    teacher = (await create_users(uow))[0]
    token = create_access_token(owner.as_short())
    workspace = await create_workspace(uow, owner.id)
    await add_user_to_workspace(uow, workspace.id, teacher.id, WorkspaceMemberRoleEnum.TEACHER)

    async with uow.connection():
        members = await uow.workspace_members.get_list(WorkspaceMemberFiltersDTO(workspace_id=workspace.id))
        teacher_member = [m for m in members if m.user_id == teacher.id][0]

    data = TransferOwnershipDTO(member_id=teacher_member.id)
    result = await transfer_ownership(workspace.id, data, token)
    assert result.id == workspace.id

    async with uow.connection():
        new_owner_member = await uow.workspace_members.get_by_user_and_workspace(teacher.id, workspace.id)
        old_owner_member = await uow.workspace_members.get_by_user_and_workspace(owner.id, workspace.id)
        assert new_owner_member.role == WorkspaceMemberRoleEnum.OWNER
        assert old_owner_member.role == WorkspaceMemberRoleEnum.TEACHER


async def test__failed__not_owner(uow, request_transfer_ownership):
    owner = (await create_users(uow))[0]
    teacher = (await create_users(uow))[0]
    token = create_access_token(teacher.as_short())
    workspace = await create_workspace(uow, owner.id)
    await add_user_to_workspace(uow, workspace.id, teacher.id, WorkspaceMemberRoleEnum.TEACHER)

    async with uow.connection():
        members = await uow.workspace_members.get_list(WorkspaceMemberFiltersDTO(workspace_id=workspace.id))
        teacher_member = [m for m in members if m.user_id == teacher.id][0]

    data = TransferOwnershipDTO(member_id=teacher_member.id)
    response = await request_transfer_ownership(workspace.id, data, token)
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json()["code"] == "role_permissions"


async def test__failed__self_transfer(uow, request_transfer_ownership):
    owner = (await create_users(uow))[0]
    token = create_access_token(owner.as_short())
    workspace = await create_workspace(uow, owner.id)

    async with uow.connection():
        members = await uow.workspace_members.get_list(WorkspaceMemberFiltersDTO(workspace_id=workspace.id))
        owner_member = [m for m in members if m.user_id == owner.id][0]

    data = TransferOwnershipDTO(member_id=owner_member.id)
    response = await request_transfer_ownership(workspace.id, data, token)
    assert response.status_code == status.HTTP_409_CONFLICT
    assert response.json()["code"] == "self_transfer_disabled"


async def test__failed__member_not_in_workspace(uow, request_transfer_ownership):
    owner = (await create_users(uow))[0]
    token = create_access_token(owner.as_short())
    workspace = await create_workspace(uow, owner.id)
    data = TransferOwnershipDTO(member_id=9999)

    response = await request_transfer_ownership(workspace.id, data, token)
    assert response.status_code == status.HTTP_404_NOT_FOUND


async def test__failed__unauthorized(request_transfer_ownership):
    data = TransferOwnershipDTO(member_id=1)
    response = await request_transfer_ownership(1, data, token="invalid")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
