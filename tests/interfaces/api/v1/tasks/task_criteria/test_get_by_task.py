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
def request_get_task_criteria(client: AsyncClient):
    async def inner(task_id: int, token: str) -> Response:
        return await client.get(
            f"/api/v1/tasks/{task_id}/criteria",
            headers={"Authorization": f"Bearer {token}"},
        )

    return inner


@pytest_asyncio.fixture()
def get_task_criteria(request_get_task_criteria):
    async def inner(task_id: int, token: str) -> list[TaskCriteriaResponseDTO]:
        response = await request_get_task_criteria(task_id, token)
        assert response.status_code == status.HTTP_200_OK
        return [TaskCriteriaResponseDTO.model_validate(item) for item in response.json()]

    return inner


async def test__success__by_owner(uow, get_task_criteria):
    user = (await create_users(uow))[0]
    token = create_access_token(user.as_short())
    workspace = await create_workspace(uow, user.id)
    task = await create_task(uow, workspace.id, user.id)
    criteria = await create_criteria(uow, user.id, size=3)

    for criterion in criteria:
        data: TaskCriteriaCreateDTO = TaskCriteriaFactory.build(task_id=task.id, criterion_id=criterion.id)
        async with uow.connection():
            await uow.task_criteria.create(data)

    task_criteria = await get_task_criteria(task.id, token)
    assert len(task_criteria) == 3
    assert all(tc.task_id == task.id for tc in task_criteria)


async def test__success__empty_list(uow, get_task_criteria):
    user = (await create_users(uow))[0]
    token = create_access_token(user.as_short())
    workspace = await create_workspace(uow, user.id)
    task = await create_task(uow, workspace.id, user.id)

    task_criteria = await get_task_criteria(task.id, token)
    assert len(task_criteria) == 0


async def test__failed__unauthorized(request_get_task_criteria):
    response = await request_get_task_criteria(task_id=1, token="invalid")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
