from fastapi import status
from httpx import AsyncClient, Response
import pytest_asyncio

from src.dto.workspaces.workspace import WorkspaceResponseDTO
from src.infrastructure.auth import create_access_token
from tests.helpers.users import create_users
from tests.helpers.workspaces import create_workspace


@pytest_asyncio.fixture()
def request_get_workspace(client: AsyncClient):
    async def inner(workspace_id: int, token: str) -> Response:
        return await client.get(
            f"/api/v1/workspaces/{workspace_id}",
            headers={"Authorization": f"Bearer {token}"},
        )

    return inner


@pytest_asyncio.fixture()
def get_workspace(request_get_workspace):
    async def inner(workspace_id: int, token: str) -> WorkspaceResponseDTO:
        response = await request_get_workspace(workspace_id, token)
        assert response.status_code == status.HTTP_200_OK
        return WorkspaceResponseDTO.model_validate_json(response.text)

    return inner


async def test__success(uow, get_workspace):
    user = (await create_users(uow))[0]
    token = create_access_token(user.as_short())
    workspace = await create_workspace(uow, user.id)

    result = await get_workspace(workspace.id, token)
    assert result.id == workspace.id
    assert result.name == workspace.name
    assert result.description == workspace.description


async def test__failed__not_member(uow, request_get_workspace):
    user = (await create_users(uow))[0]
    workspace = await create_workspace(uow, user.id)
    other_user = (await create_users(uow))[0]
    token = create_access_token(other_user.as_short())

    response = await request_get_workspace(workspace.id, token)
    assert response.status_code == status.HTTP_403_FORBIDDEN, response.text
    assert response.json()["code"] == "user_not_member"


async def test__failed__workspace_not_found(uow, request_get_workspace):
    user = (await create_users(uow))[0]
    token = create_access_token(user.as_short())

    response = await request_get_workspace(9999, token)
    assert response.status_code == status.HTTP_404_NOT_FOUND


async def test__failed__unauthorized(request_get_workspace):
    response = await request_get_workspace(1, token="invalid")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
