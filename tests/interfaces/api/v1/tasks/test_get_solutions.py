from fastapi import status
from httpx import AsyncClient, Response
import pytest_asyncio
from tests.helpers.workspaces import create_workspace_with_task
from tests.helpers.solutions import create_github_solution
from tests.helpers.users import create_users

from src.infrastructure.auth import create_access_token


@pytest_asyncio.fixture()
async def request_get_solutions_by_task(client: AsyncClient):
    async def inner(task_id: int, token: str) -> Response:
        return await client.get(
            f"/api/v1/tasks/{task_id}/solutions",
            headers={"Authorization": f"Bearer {token}"},
        )

    return inner



async def test__success__get_list_by_task(uow, request_get_solutions_by_task):
    user = (await create_users(uow))[0]
    workspace, task = await create_workspace_with_task(uow, user.id)
    token = create_access_token(user.as_short())

    await create_github_solution(uow, task.id, user.id)

    response = await request_get_solutions_by_task(task_id=task.id, token=token)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) == 1


async def test__success__get_list_empty(uow, request_get_solutions_by_task):
    user = (await create_users(uow))[0]
    workspace, task = await create_workspace_with_task(uow, user.id)
    token = create_access_token(user.as_short())

    response = await request_get_solutions_by_task(task_id=task.id, token=token)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) == 0


async def test__failed__not_workspace_member(uow, request_get_solutions_by_task):
    user = (await create_users(uow))[0]
    workspace, task = await create_workspace_with_task(uow, user.id)

    other_user = (await create_users(uow))[0]
    other_token = create_access_token(other_user.as_short())

    response = await request_get_solutions_by_task(task_id=task.id, token=other_token)
    assert response.status_code == status.HTTP_403_FORBIDDEN


async def test__failed__task_not_found(uow, request_get_solutions_by_task):
    user = (await create_users(uow))[0]
    token = create_access_token(user.as_short())

    response = await request_get_solutions_by_task(task_id=99999, token=token)
    assert response.status_code == status.HTTP_404_NOT_FOUND
