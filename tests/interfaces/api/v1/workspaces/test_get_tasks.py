from fastapi import status
from httpx import AsyncClient, Response
import pytest_asyncio

from src.infrastructure.auth import create_access_token
from tests.helpers.users import create_users
from tests.helpers.workspaces import create_workspace


@pytest_asyncio.fixture()
def request_get_tasks(client: AsyncClient):
    async def inner(workspace_id: int, token: str) -> Response:
        return await client.get(
            f"/api/v1/workspaces/{workspace_id}/tasks",
            headers={"Authorization": f"Bearer {token}"},
        )

    return inner


async def test__success(uow, request_get_tasks):
    user = (await create_users(uow))[0]
    token = create_access_token(user.as_short())
    workspace = await create_workspace(uow, user.id)

    response = await request_get_tasks(workspace.id, token)
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == []


async def test__failed__not_member(uow, request_get_tasks):
    user = (await create_users(uow))[0]
    other_user = (await create_users(uow))[0]
    token = create_access_token(other_user.as_short())
    workspace = await create_workspace(uow, user.id)

    response = await request_get_tasks(workspace.id, token)
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json()["code"] == "user_not_member"


async def test__failed__unauthorized(request_get_tasks):
    response = await request_get_tasks(1, token="invalid")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
