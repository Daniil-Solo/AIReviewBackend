from fastapi import status
from httpx import AsyncClient, Response
import pytest_asyncio

from src.constants.workspaces import WorkspaceMemberRoleEnum
from src.infrastructure.auth import create_access_token
from tests.factories.solutions import SolutionGitHubFactory
from tests.helpers.criteria import create_criteria
from tests.helpers.tasks import create_task, create_task_criterion
from tests.helpers.users import create_users
from tests.helpers.workspaces import add_user_to_workspace, create_workspace


@pytest_asyncio.fixture()
async def request_create_criteria_check(client: AsyncClient):
    async def inner(
        solution_id: int,
        task_criterion_id: int,
        is_passed: bool,
        token: str,
        comment: str = "",
    ) -> Response:
        return await client.post(
            f"/api/v1/solutions/{solution_id}/criteria-checks",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "solution_id": solution_id,
                "task_criterion_id": task_criterion_id,
                "is_passed": is_passed,
                "comment": comment,
            },
        )

    return inner


async def test__success__by_owner(uow, request_create_criteria_check):
    user = (await create_users(uow))[0]
    workspace = await create_workspace(uow, user.id)
    task = await create_task(uow, workspace.id, user.id)
    token = create_access_token(user.as_short())

    criteria = (await create_criteria(uow, user.id, size=1))[0]
    task_criterion = await create_task_criterion(uow, task.id, criteria.id)

    solution_data = SolutionGitHubFactory.build(task_id=task.id)
    async with uow.connection():
        solution = await uow.solutions.create(solution_data, user.id)

    response = await request_create_criteria_check(
        solution_id=solution.id,
        task_criterion_id=task_criterion.id,
        is_passed=True,
        token=token,
        comment="Хорошая работа",
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["message"] == "Фидбек оставлен"


async def test__success__by_teacher(uow, request_create_criteria_check):
    owner = (await create_users(uow))[0]
    workspace = await create_workspace(uow, owner.id)
    task = await create_task(uow, workspace.id, owner.id)

    teacher = (await create_users(uow))[0]
    await add_user_to_workspace(uow, workspace.id, teacher.id, role=WorkspaceMemberRoleEnum.TEACHER)
    teacher_token = create_access_token(teacher.as_short())

    criteria = (await create_criteria(uow, owner.id, size=1))[0]
    task_criterion = await create_task_criterion(uow, task.id, criteria.id)

    solution_data = SolutionGitHubFactory.build(task_id=task.id)
    async with uow.connection():
        solution = await uow.solutions.create(solution_data, teacher.id)

    response = await request_create_criteria_check(
        solution_id=solution.id,
        task_criterion_id=task_criterion.id,
        is_passed=True,
        token=teacher_token,
        comment="Хорошая работа",
    )
    assert response.status_code == status.HTTP_200_OK


async def test__failed__by_student(uow, request_create_criteria_check):
    owner = (await create_users(uow))[0]
    workspace = await create_workspace(uow, owner.id)
    task = await create_task(uow, workspace.id, owner.id)

    student = (await create_users(uow))[0]
    await add_user_to_workspace(uow, workspace.id, student.id, role=WorkspaceMemberRoleEnum.STUDENT)
    student_token = create_access_token(student.as_short())

    criteria = (await create_criteria(uow, owner.id, size=1))[0]
    task_criterion = await create_task_criterion(uow, task.id, criteria.id)

    solution_data = SolutionGitHubFactory.build(task_id=task.id)
    async with uow.connection():
        solution = await uow.solutions.create(solution_data, student.id)

    response = await request_create_criteria_check(
        solution_id=solution.id,
        task_criterion_id=task_criterion.id,
        is_passed=True,
        token=student_token,
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN


async def test__failed__not_workspace_member(uow, request_create_criteria_check):
    owner = (await create_users(uow))[0]
    workspace = await create_workspace(uow, owner.id)
    task = await create_task(uow, workspace.id, owner.id)

    other_user = (await create_users(uow))[0]
    other_token = create_access_token(other_user.as_short())

    criteria = (await create_criteria(uow, owner.id, size=1))[0]
    task_criterion = await create_task_criterion(uow, task.id, criteria.id)

    solution_data = SolutionGitHubFactory.build(task_id=task.id)
    async with uow.connection():
        solution = await uow.solutions.create(solution_data, owner.id)

    response = await request_create_criteria_check(
        solution_id=solution.id,
        task_criterion_id=task_criterion.id,
        is_passed=True,
        token=other_token,
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN


async def test__failed__solution_not_found(uow, request_create_criteria_check):
    user = (await create_users(uow))[0]
    token = create_access_token(user.as_short())

    response = await request_create_criteria_check(
        solution_id=99999,
        task_criterion_id=1,
        is_passed=True,
        token=token,
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND

