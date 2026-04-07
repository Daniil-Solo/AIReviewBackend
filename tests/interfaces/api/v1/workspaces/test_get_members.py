from fastapi import status
from httpx import AsyncClient, Response
import pytest_asyncio

from src.constants.workspaces import WorkspaceMemberRoleEnum
from src.dto.workspaces.member import WorkspaceMemberResponseDTO
from src.infrastructure.auth import create_access_token
from tests.helpers.users import create_users
from tests.helpers.workspaces import create_workspace, add_user_to_workspace


@pytest_asyncio.fixture()
def request_get_members(client: AsyncClient):
    async def inner(workspace_id: int, token: str) -> Response:
        return await client.get(
            f"/api/v1/workspaces/{workspace_id}/members",
            headers={"Authorization": f"Bearer {token}"},
        )

    return inner


@pytest_asyncio.fixture()
def get_members(request_get_members):
    async def inner(workspace_id: int, token: str) -> list[WorkspaceMemberResponseDTO]:
        response = await request_get_members(workspace_id, token)
        assert response.status_code == status.HTTP_200_OK
        return [WorkspaceMemberResponseDTO.model_validate(m) for m in response.json()]

    return inner


async def test__success__owner(uow, get_members):
    owner = (await create_users(uow))[0]
    token = create_access_token(owner.as_short())
    workspace = await create_workspace(uow, owner.id)

    members = await get_members(workspace.id, token)
    assert len(members) == 1
    assert members[0].user_id == owner.id
    assert members[0].role == WorkspaceMemberRoleEnum.OWNER


async def test__success__multiple_members(uow, get_members):
    owner = (await create_users(uow))[0]
    student1 = (await create_users(uow))[0]
    student2 = (await create_users(uow))[0]
    token = create_access_token(owner.as_short())
    workspace = await create_workspace(uow, owner.id)
    await add_user_to_workspace(uow, workspace.id, student1.id, WorkspaceMemberRoleEnum.STUDENT)
    await add_user_to_workspace(uow, workspace.id, student2.id, WorkspaceMemberRoleEnum.STUDENT)

    members = await get_members(workspace.id, token)
    assert len(members) == 3


async def test__success__student_can_view(uow, get_members):
    owner = (await create_users(uow))[0]
    student = (await create_users(uow))[0]
    token = create_access_token(student.as_short())
    workspace = await create_workspace(uow, owner.id)
    await add_user_to_workspace(uow, workspace.id, student.id, WorkspaceMemberRoleEnum.STUDENT)

    members = await get_members(workspace.id, token)
    assert len(members) == 2


async def test__failed__not_member(uow, request_get_members):
    user = (await create_users(uow))[0]
    other_user = (await create_users(uow))[0]
    token = create_access_token(other_user.as_short())
    workspace = await create_workspace(uow, user.id)

    response = await request_get_members(workspace.id, token)
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json()["code"] == "user_not_member"


async def test__failed__unauthorized(request_get_members):
    response = await request_get_members(1, token="invalid")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
