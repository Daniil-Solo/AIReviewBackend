from fastapi import status
from httpx import AsyncClient, Response
import pytest_asyncio

from src.infrastructure.auth import create_access_token
from tests.helpers.tasks import create_task
from tests.helpers.users import create_users
from tests.helpers.workspaces import create_workspace


@pytest_asyncio.fixture()
def request_delete_task(client: AsyncClient):
    async def inner(task_id: int, token: str) -> Response:
        return await client.delete(
            f"/api/v1/tasks/{task_id}",
            headers={"Authorization": f"Bearer {token}"},
        )

    return inner


async def test__success(uow, request_delete_task):
    user = (await create_users(uow))[0]
    token = create_access_token(user.as_short())
    workspace = await create_workspace(uow, user.id)
    task = await create_task(uow, user.id, workspace.id, name="Task to Delete")

    response = await request_delete_task(task.id, token)
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["message"] == "Задача удалена"


async def test__failed__not_found(uow, request_delete_task):
    user = (await create_users(uow))[0]
    token = create_access_token(user.as_short())

    response = await request_delete_task(9999, token)
    assert response.status_code == status.HTTP_404_NOT_FOUND


async def test__failed__unauthorized(request_delete_task):
    response = await request_delete_task(1, token="invalid")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
