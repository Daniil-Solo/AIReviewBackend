from fastapi import status
from httpx import AsyncClient, Response
import pytest_asyncio

from src.dto.tasks.task_criteria import TaskCriteriaCreateDTO
from src.infrastructure.auth import create_access_token
from tests.factories.tasks import TaskCriteriaFactory
from tests.helpers.criteria import create_criteria
from tests.helpers.tasks import create_task
from tests.helpers.users import create_users
from tests.helpers.workspaces import create_workspace


@pytest_asyncio.fixture()
def request_delete_task_criterion(client: AsyncClient):
    async def inner(task_id: int, task_criterion_id: int, token: str) -> Response:
        return await client.delete(
            f"/api/v1/tasks/{task_id}/criteria/{task_criterion_id}",
            headers={"Authorization": f"Bearer {token}"},
        )

    return inner


async def test__success__by_owner(uow, request_delete_task_criterion):
    user = (await create_users(uow))[0]
    token = create_access_token(user.as_short())
    workspace = await create_workspace(uow, user.id)
    task = await create_task(uow, workspace.id, user.id)
    criterion = (await create_criteria(uow, user.id, size=1))[0]

    data: TaskCriteriaCreateDTO = TaskCriteriaFactory.build(task_id=task.id, criterion_id=criterion.id)
    async with uow.connection():
        task_criterion = await uow.task_criteria.create(data)

    response = await request_delete_task_criterion(task.id, task_criterion.id, token)
    assert response.status_code == status.HTTP_200_OK


async def test__failed__unauthorized(request_delete_task_criterion):
    response = await request_delete_task_criterion(task_id=1, task_criterion_id=1, token="invalid")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
