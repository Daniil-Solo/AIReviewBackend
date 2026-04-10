from fastapi import status
from httpx import AsyncClient, Response
import pytest_asyncio
from tests.helpers.workspaces import create_workspace_with_task
from tests.helpers.solutions import create_github_solution
from tests.helpers.users import create_users

from src.infrastructure.auth import create_access_token


@pytest_asyncio.fixture()
async def request_cancel_solution(client: AsyncClient):
    async def inner(solution_id: int, token: str) -> Response:
        return await client.post(
            f"/api/v1/solutions/{solution_id}/cancel",
            headers={"Authorization": f"Bearer {token}"},
        )

    return inner



async def test__success__cancel_own_solution(uow, request_cancel_solution):
    user = (await create_users(uow))[0]
    workspace, task = await create_workspace_with_task(uow, user.id)
    token = create_access_token(user.as_short())

    solution = await create_github_solution(uow, task.id, user.id)

    response = await request_cancel_solution(solution_id=solution.id, token=token)
    assert response.status_code == status.HTTP_200_OK


async def test__failed__cancel_other_solution(uow, request_cancel_solution):
    user = (await create_users(uow))[0]
    workspace, task = await create_workspace_with_task(uow, user.id)

    solution = await create_github_solution(uow, task.id, user.id)

    other_user = (await create_users(uow))[0]
    other_token = create_access_token(other_user.as_short())

    response = await request_cancel_solution(solution_id=solution.id, token=other_token)
    assert response.status_code == status.HTTP_403_FORBIDDEN


async def test__failed__cancel_not_found(uow, request_cancel_solution):
    user = (await create_users(uow))[0]
    token = create_access_token(user.as_short())

    response = await request_cancel_solution(solution_id=99999, token=token)
    assert response.status_code == status.HTTP_404_NOT_FOUND
