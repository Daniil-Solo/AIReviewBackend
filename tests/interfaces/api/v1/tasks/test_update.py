from fastapi import status
from httpx import AsyncClient, Response
import pytest_asyncio

from src.dto.tasks.tasks import TaskUpdateDTO, TaskResponseDTO
from src.infrastructure.auth import create_access_token
from tests.factories.tasks import TaskFactory, TaskUpdateFactory
from tests.helpers.tasks import create_task
from tests.helpers.users import create_users
from tests.helpers.workspaces import create_workspace


@pytest_asyncio.fixture()
def request_update_task(client: AsyncClient):
    async def inner(task_id: int, data: TaskUpdateDTO, token: str) -> Response:
        return await client.put(
            f"/api/v1/tasks/{task_id}",
            json=data.model_dump(by_alias=True),
            headers={"Authorization": f"Bearer {token}"},
        )

    return inner


@pytest_asyncio.fixture()
def update_task(request_update_task):
    async def inner(task_id: int, data: TaskUpdateDTO, token: str) -> TaskResponseDTO:
        response = await request_update_task(task_id, data, token)
        assert response.status_code == status.HTTP_200_OK
        return TaskResponseDTO.model_validate_json(response.text)

    return inner


async def test__success(uow, update_task):
    user = (await create_users(uow))[0]
    token = create_access_token(user.as_short())
    workspace = await create_workspace(uow, user.id)
    task = await create_task(uow, workspace.id, user.id)

    data: TaskUpdateDTO = TaskUpdateFactory.build(name="Updated Name")

    result = await update_task(task.id, data, token)
    assert result.name == "Updated Name"


async def test__failed__not_found(uow, request_update_task):
    user = (await create_users(uow))[0]
    token = create_access_token(user.as_short())
    data: TaskUpdateDTO = TaskUpdateFactory.build()

    response = await request_update_task(9999, data, token)
    assert response.status_code == status.HTTP_404_NOT_FOUND


async def test__failed__unauthorized(request_update_task):
    data: TaskUpdateDTO = TaskUpdateFactory.build()

    response = await request_update_task(1, data, token="invalid")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
