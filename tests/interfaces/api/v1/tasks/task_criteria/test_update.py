from fastapi import status
from httpx import AsyncClient, Response
import pytest_asyncio

from src.dto.tasks.task_criteria import TaskCriteriaCreateDTO, TaskCriteriaResponseDTO, TaskCriteriaUpdateWeightDTO
from src.infrastructure.auth import create_access_token
from tests.factories.tasks import TaskCriteriaFactory, TaskCriteriaUpdateWeightFactory
from tests.helpers.criteria import create_criteria
from tests.helpers.tasks import create_task
from tests.helpers.users import create_users
from tests.helpers.workspaces import create_workspace


@pytest_asyncio.fixture()
def request_update_task_criterion(client: AsyncClient):
    async def inner(task_id: int, task_criterion_id: int, data: TaskCriteriaUpdateWeightDTO, token: str) -> Response:
        return await client.patch(
            f"/api/v1/tasks/{task_id}/criteria/{task_criterion_id}",
            json=data.model_dump(by_alias=True),
            headers={"Authorization": f"Bearer {token}"},
        )

    return inner


@pytest_asyncio.fixture()
def update_task_criterion(request_update_task_criterion):
    async def inner(
        task_id: int, task_criterion_id: int, data: TaskCriteriaUpdateWeightDTO, token: str
    ) -> TaskCriteriaResponseDTO:
        response = await request_update_task_criterion(task_id, task_criterion_id, data, token)
        assert response.status_code == status.HTTP_200_OK
        return TaskCriteriaResponseDTO.model_validate_json(response.text)

    return inner


async def test__success__by_owner(uow, update_task_criterion):
    user = (await create_users(uow))[0]
    token = create_access_token(user.as_short())
    workspace = await create_workspace(uow, user.id)
    task = await create_task(uow, workspace.id, user.id)
    criterion = (await create_criteria(uow, user.id, size=1))[0]

    data: TaskCriteriaCreateDTO = TaskCriteriaFactory.build(task_id=task.id, criterion_id=criterion.id, weight=0.5)
    async with uow.connection():
        task_criterion = await uow.task_criteria.create(data)

    update_data: TaskCriteriaUpdateWeightDTO = TaskCriteriaUpdateWeightFactory.build(weight=0.8)

    updated = await update_task_criterion(task.id, task_criterion.id, update_data, token)
    assert updated.weight == update_data.weight


async def test__failed__unauthorized(request_update_task_criterion):
    data: TaskCriteriaUpdateWeightDTO = TaskCriteriaUpdateWeightFactory.build()

    response = await request_update_task_criterion(task_id=1, task_criterion_id=1, data=data, token="invalid")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
