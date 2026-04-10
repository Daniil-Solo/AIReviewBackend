from fastapi import status
from httpx import AsyncClient, Response
import pytest_asyncio

from src.dto.tasks.tasks import TaskCreateDTO, TaskResponseDTO
from src.infrastructure.auth import create_access_token
from tests.factories.tasks import TaskFactory
from tests.helpers.users import create_users
from tests.helpers.workspaces import create_workspace


@pytest_asyncio.fixture()
def request_create_task(client: AsyncClient):
    async def inner(data: TaskCreateDTO, token: str) -> Response:
        return await client.post(
            "/api/v1/tasks",
            json=data.model_dump(by_alias=True),
            headers={"Authorization": f"Bearer {token}"},
        )

    return inner


@pytest_asyncio.fixture()
def create_task(request_create_task):
    async def inner(data: TaskCreateDTO, token: str) -> TaskResponseDTO:
        response = await request_create_task(data, token)
        assert response.status_code == status.HTTP_200_OK
        return TaskResponseDTO.model_validate_json(response.text)

    return inner


async def test__success__by_owner(uow, create_task):
    user = (await create_users(uow))[0]
    token = create_access_token(user.as_short())
    workspace = await create_workspace(uow, user.id)
    data: TaskCreateDTO = TaskFactory.build(workspace_id=workspace.id)

    task = await create_task(data, token)
    assert task.name == data.name
    assert task.description == data.description
    assert task.workspace_id == workspace.id
    assert task.created_by == user.id


async def test__failed__unauthorized(request_create_task):
    data: TaskCreateDTO = TaskFactory.build()

    response = await request_create_task(data, token="invalid")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
