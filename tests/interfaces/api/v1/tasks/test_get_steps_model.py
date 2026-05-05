from fastapi import status
from httpx import AsyncClient, Response
import pytest_asyncio

from src.dto.custom_models.custom_models import TaskStepsModelDTO
from src.infrastructure.auth import create_access_token
from tests.helpers.custom_models import create_custom_model
from tests.helpers.tasks import create_task
from tests.helpers.users import create_users
from tests.helpers.workspaces import create_workspace


@pytest_asyncio.fixture()
def request_get_task_steps_model(client: AsyncClient):
    async def inner(task_id: int, token: str) -> Response:
        return await client.get(
            f"/api/v1/tasks/{task_id}/steps-models",
            headers={"Authorization": f"Bearer {token}"},
        )

    return inner


@pytest_asyncio.fixture()
def get_task_steps_model(request_get_task_steps_model):
    async def inner(task_id: int, token: str) -> TaskStepsModelDTO:
        response = await request_get_task_steps_model(task_id, token)
        assert response.status_code == status.HTTP_200_OK
        return TaskStepsModelDTO.model_validate_json(response.text)

    return inner


async def test__success__not_set(uow, get_task_steps_model):
    user = (await create_users(uow))[0]
    token = create_access_token(user.as_short())
    workspace = await create_workspace(uow, user.id)
    task = await create_task(uow, workspace.id, user.id)

    result = await get_task_steps_model(task.id, token)
    assert result.task_id == task.id
    assert all(v is None for v in result.steps.values())


async def test__failed__task_not_found(uow, request_get_task_steps_model):
    user = (await create_users(uow))[0]
    token = create_access_token(user.as_short())

    response = await request_get_task_steps_model(9999, token)
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["code"] == "not_found"


async def test__failed__not_member(uow, request_get_task_steps_model):
    user = (await create_users(uow))[0]
    workspace = await create_workspace(uow, user.id)
    task = await create_task(uow, workspace.id, user.id)
    other_user = (await create_users(uow))[0]
    token = create_access_token(other_user.as_short())

    response = await request_get_task_steps_model(task.id, token)
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json()["code"] == "user_not_member"


async def test__failed__unauthorized(request_get_task_steps_model):
    response = await request_get_task_steps_model(1, token="invalid")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
