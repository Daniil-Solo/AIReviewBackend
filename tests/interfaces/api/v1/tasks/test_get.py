from fastapi import status
from httpx import AsyncClient, Response
import pytest_asyncio

from src.dto.tasks.tasks import TaskResponseDTO
from src.infrastructure.auth import create_access_token
from tests.helpers.tasks import create_task
from tests.helpers.users import create_users
from tests.helpers.workspaces import create_workspace, add_user_to_workspace
from src.constants.workspaces import WorkspaceMemberRoleEnum


@pytest_asyncio.fixture()
def request_get_task(client: AsyncClient):
    async def inner(task_id: int, token: str) -> Response:
        return await client.get(
            f"/api/v1/tasks/{task_id}",
            headers={"Authorization": f"Bearer {token}"},
        )

    return inner


@pytest_asyncio.fixture()
def get_task(request_get_task):
    async def inner(task_id: int, token: str) -> TaskResponseDTO:
        response = await request_get_task(task_id, token)
        assert response.status_code == status.HTTP_200_OK
        return TaskResponseDTO.model_validate_json(response.text)

    return inner


async def test__success(uow, get_task):
    user = (await create_users(uow))[0]
    token = create_access_token(user.as_short())
    workspace = await create_workspace(uow, user.id)
    task = await create_task(uow, user.id, workspace.id, name="Test Task")

    result = await get_task(task.id, token)
    assert result.name == "Test Task"
    assert result.workspace_id == workspace.id


async def test__failed__not_found(uow, request_get_task):
    user = (await create_users(uow))[0]
    token = create_access_token(user.as_short())

    response = await request_get_task(9999, token)
    assert response.status_code == status.HTTP_404_NOT_FOUND


async def test__failed__unauthorized(request_get_task):
    response = await request_get_task(1, token="invalid")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
