from fastapi import status
from httpx import AsyncClient, Response
import pytest_asyncio

from tests.helpers.workspaces import create_workspace_with_task
from tests.helpers.solutions import create_github_solution, create_solution_criteria_check
from tests.helpers.criteria import create_criteria
from tests.helpers.tasks import create_task_criterion
from tests.helpers.users import create_users

from src.dto.solutions.wind_rose import WindRosePointDTO
from src.infrastructure.auth import create_access_token


@pytest_asyncio.fixture()
def request_get_wind_rose(client: AsyncClient):
    async def inner(solution_id: int, token: str) -> Response:
        return await client.get(
            f"/api/v1/solutions/{solution_id}/wind-rose",
            headers={"Authorization": f"Bearer {token}"},
        )

    return inner


@pytest_asyncio.fixture()
def get_wind_rose(request_get_wind_rose):
    async def inner(solution_id: int, token: str) -> list[WindRosePointDTO]:
        response = await request_get_wind_rose(solution_id, token)
        assert response.status_code == status.HTTP_200_OK
        return [WindRosePointDTO.model_validate_json(item) for item in response.json()]

    return inner


async def test__success__with_tags(uow, get_wind_rose):
    user = (await create_users(uow))[0]
    workspace, task = await create_workspace_with_task(uow, user.id)
    token = create_access_token(user.as_short())

    criteria_1 = (await create_criteria(uow, user.id, tags=["style"]))[0]
    criteria_2 = (await create_criteria(uow, user.id, tags=["best_practice"]))[0]

    task_criterion_1 = await create_task_criterion(uow, task.id, criteria_1.id)
    task_criterion_2 = await create_task_criterion(uow, task.id, criteria_2.id)

    solution = await create_github_solution(uow, task.id, user.id)

    await create_solution_criteria_check(uow, task_criterion_1.id, solution.id, is_passed=True)
    await create_solution_criteria_check(uow, task_criterion_2.id, solution.id, is_passed=False)

    wind_rose = await get_wind_rose(solution.id, token)

    assert len(wind_rose) == 2

    style_point = next(p for p in wind_rose if p.tag == "style")
    assert style_point.value == 1.0
    assert style_point.count == 1

    best_practice_point = next(p for p in wind_rose if p.tag == "best_practice")
    assert best_practice_point.value == 0.0
    assert best_practice_point.count == 1


async def test__success__empty(uow, get_wind_rose):
    user = (await create_users(uow))[0]
    workspace, task = await create_workspace_with_task(uow, user.id)
    token = create_access_token(user.as_short())

    solution = await create_github_solution(uow, task.id, user.id)

    wind_rose = await get_wind_rose(solution.id, token)

    assert len(wind_rose) == 0


async def test__failed__unauthorized(request_get_wind_rose):
    response = await request_get_wind_rose(solution_id=1, token="invalid")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


async def test__failed__forbidden(uow, request_get_wind_rose):
    user = (await create_users(uow))[0]
    workspace, task = await create_workspace_with_task(uow, user.id)

    other_user = (await create_users(uow))[0]
    other_token = create_access_token(other_user.as_short())

    solution = await create_github_solution(uow, task.id, user.id)

    response = await request_get_wind_rose(solution_id=solution.id, token=other_token)
    assert response.status_code == status.HTTP_403_FORBIDDEN


async def test__success__author_access(uow, get_wind_rose):
    user = (await create_users(uow))[0]
    workspace, task = await create_workspace_with_task(uow, user.id)
    token = create_access_token(user.as_short())

    criteria = (await create_criteria(uow, user.id, tags=["code_style"]))[0]
    task_criterion = await create_task_criterion(uow, task.id, criteria.id)

    solution = await create_github_solution(uow, task.id, user.id)
    await create_solution_criteria_check(uow, task_criterion.id, solution.id, is_passed=True)

    wind_rose = await get_wind_rose(solution.id, token)

    assert len(wind_rose) == 1
    assert wind_rose[0].tag == "code_style"


async def test__failed__solution_not_found(uow, request_get_wind_rose):
    user = (await create_users(uow))[0]
    token = create_access_token(user.as_short())

    response = await request_get_wind_rose(solution_id=99999, token=token)
    assert response.status_code == status.HTTP_404_NOT_FOUND
