from fastapi import status
from httpx import AsyncClient, Response
import pytest_asyncio

from src.dto.tasks.tasks import TaskResponseDTO
from src.infrastructure.auth import create_access_token
from tests.helpers.tasks import create_task
from tests.helpers.users import create_users
from tests.helpers.workspaces import create_workspace


@pytest_asyncio.fixture()
def request_get_public_task(client: AsyncClient):
    async def inner(task_id: int, token: str) -> Response:
        return await client.get(
            f"/api/v1/tasks/{task_id}/public",
            headers={"Authorization": f"Bearer {token}"},
        )

    return inner


@pytest_asyncio.fixture()
def get_public_task(request_get_public_task):
    async def inner(task_id: int, token: str) -> TaskResponseDTO:
        response = await request_get_public_task(task_id, token)
        assert response.status_code == status.HTTP_200_OK
        return TaskResponseDTO.model_validate_json(response.text)

    return inner


async def test__success__active_task(uow, get_public_task):
    user = (await create_users(uow))[0]
    token = create_access_token(user.as_short())
    workspace = await create_workspace(uow, user.id)
    task = await create_task(uow, workspace.id, user.id, is_active=True)

    result = await get_public_task(task.id, token)
    assert result.name == task.name
    assert result.description == task.description
    assert result.is_active


async def test__failed__not_active(uow, request_get_public_task):
    user = (await create_users(uow))[0]
    token = create_access_token(user.as_short())
    workspace = await create_workspace(uow, user.id)
    task = await create_task(uow, workspace.id, user.id, is_active=False)

    response = await request_get_public_task(task.id, token)
    assert response.status_code == status.HTTP_404_NOT_FOUND


async def test__failed__not_found(uow, request_get_public_task):
    user = (await create_users(uow))[0]
    token = create_access_token(user.as_short())

    response = await request_get_public_task(9999, token)
    assert response.status_code == status.HTTP_404_NOT_FOUND


async def test__failed__unauthorized(request_get_public_task):
    response = await request_get_public_task(1, token="invalid")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
