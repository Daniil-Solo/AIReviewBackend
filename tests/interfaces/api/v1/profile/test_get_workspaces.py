from fastapi import status
from httpx import AsyncClient, Response
import pytest_asyncio
from pydantic import TypeAdapter

from src.dto.workspaces.workspace import UserWorkspaceResponseDTO
from src.infrastructure.auth import create_access_token
from tests.helpers.users import create_users
from tests.helpers.workspaces import create_workspace


@pytest_asyncio.fixture()
def request_get_profile_workspaces(client: AsyncClient):
    async def inner(token: str) -> Response:
        return await client.get(
            "/api/v1/profile/workspaces",
            headers={"Authorization": f"Bearer {token}"},
        )

    return inner


@pytest_asyncio.fixture()
def get_profile_workspaces(request_get_profile_workspaces):
    async def inner(token: str) -> list[UserWorkspaceResponseDTO]:
        response = await request_get_profile_workspaces(token)
        assert response.status_code == status.HTTP_200_OK
        return TypeAdapter(list[UserWorkspaceResponseDTO]).validate_json(response.text)

    return inner


async def test__success(uow, get_profile_workspaces):
    user = (await create_users(uow))[0]
    token = create_access_token(user.as_short())

    workspace1 = await create_workspace(uow, user.id, "ws1")
    workspace2 = await create_workspace(uow, user.id, "ws2")

    result = await get_profile_workspaces(token)

    workspace_ids = [w.workspace.id for w in result]
    assert workspace1.id in workspace_ids
    assert workspace2.id in workspace_ids


async def test__success__empty_list(uow, request_get_profile_workspaces):
    user = (await create_users(uow))[0]
    token = create_access_token(user.as_short())

    response = await request_get_profile_workspaces(token)
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == []


async def test__failed__unauthorized(request_get_profile_workspaces):
    response = await request_get_profile_workspaces(token="invalid")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
