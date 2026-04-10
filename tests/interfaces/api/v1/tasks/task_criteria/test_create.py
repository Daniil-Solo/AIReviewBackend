from fastapi import status
from httpx import AsyncClient, Response
import pytest_asyncio

from src.dto.tasks.task_criteria import TaskCriteriaCreateDTO, TaskCriteriaResponseDTO
from src.infrastructure.auth import create_access_token
from tests.factories.tasks import TaskCriteriaFactory
from tests.helpers.criteria import create_criteria
from tests.helpers.tasks import create_task
from tests.helpers.users import create_users
from tests.helpers.workspaces import create_workspace


@pytest_asyncio.fixture()
def request_create_task_criterion(client: AsyncClient):
    async def inner(task_id: int, data: TaskCriteriaCreateDTO, token: str) -> Response:
        return await client.post(
            f"/api/v1/tasks/{task_id}/criteria",
            json=data.model_dump(by_alias=True),
            headers={"Authorization": f"Bearer {token}"},
        )

    return inner


@pytest_asyncio.fixture()
def create_task_criterion(request_create_task_criterion):
    async def inner(task_id: int, data: TaskCriteriaCreateDTO, token: str) -> TaskCriteriaResponseDTO:
        response = await request_create_task_criterion(task_id, data, token)
        assert response.status_code == status.HTTP_200_OK
        return TaskCriteriaResponseDTO.model_validate_json(response.text)

    return inner


async def test__success__by_owner(uow, create_task_criterion):
    user = (await create_users(uow))[0]
    token = create_access_token(user.as_short())
    workspace = await create_workspace(uow, user.id)
    task = await create_task(uow, workspace.id, user.id)
    criterion = (await create_criteria(uow, user.id, size=1))[0]

    data: TaskCriteriaCreateDTO = TaskCriteriaFactory.build(task_id=task.id, criterion_id=criterion.id)

    task_criterion = await create_task_criterion(task.id, data, token)
    assert task_criterion.task_id == task.id
    assert task_criterion.criterion_id == criterion.id
    assert task_criterion.weight == data.weight


async def test__failed__unauthorized(request_create_task_criterion):
    data: TaskCriteriaCreateDTO = TaskCriteriaFactory.build(task_id=9999, criterion_id=9999)

    response = await request_create_task_criterion(task_id=9999, data=data, token="invalid")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
