from fastapi import status
from httpx import AsyncClient, Response
import pytest_asyncio

from src.constants.ai_review import SolutionFormatEnum, SolutionStatusEnum
from tests.factories.solutions import SolutionGitHubFactory
from tests.helpers.workspaces import create_workspace_with_task
from tests.helpers.users import create_users

from src.dto.solutions.solutions import SolutionShortResponseDTO, SolutionCreateDTO
from src.infrastructure.auth import create_access_token


@pytest_asyncio.fixture()
async def request_create_solution(client: AsyncClient):
    async def inner(data: SolutionCreateDTO, token: str) -> Response:
        return await client.post(
            "/api/v1/solutions",
            data=data.model_dump(),
            headers={"Authorization": f"Bearer {token}"},
        )
    return inner


@pytest_asyncio.fixture()
async def create_solution(request_create_solution):
    async def inner(data: SolutionCreateDTO, token: str) -> SolutionShortResponseDTO:
        response = await request_create_solution(data, token)
        assert response.status_code == status.HTTP_200_OK
        return SolutionShortResponseDTO.model_validate_json(response.text)
    return inner



async def test__success(uow, create_solution):
    user = (await create_users(uow))[0]
    workspace, task = await create_workspace_with_task(uow, user.id)
    token = create_access_token(user.as_short())

    solution = await create_solution(
        SolutionGitHubFactory.build(task_id=task.id),
        token=token,
    )
    assert solution.task_id == task.id
    assert solution.format == solution.format
    assert solution.link == solution.link
    assert solution.status == SolutionStatusEnum.CREATED



async def test__failed__not_member(uow, request_create_solution):
    user = (await create_users(uow))[0]
    workspace, task = await create_workspace_with_task(uow, user.id)

    other_user = (await create_users(uow))[0]
    token = create_access_token(other_user.as_short())

    response = await request_create_solution(
        SolutionGitHubFactory.build(task_id=task.id),
        token=token,
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN


async def test__failed__task_not_found(uow, request_create_solution):
    user = (await create_users(uow))[0]
    token = create_access_token(user.as_short())

    response = await request_create_solution(
        SolutionGitHubFactory.build(task_id=9999),
        token=token,
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND
