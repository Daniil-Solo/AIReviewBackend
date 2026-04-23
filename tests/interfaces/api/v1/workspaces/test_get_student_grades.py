import pytest_asyncio
from fastapi import status
from httpx import AsyncClient, Response

from src.constants.ai_review import  SolutionStatusEnum
from src.constants.workspaces import WorkspaceMemberRoleEnum
from src.dto.solutions.solutions import SolutionUpdateDTO
from src.dto.workspaces.student_grades import StudentGradesDTO
from src.infrastructure.auth import create_access_token
from tests.factories.tasks import TaskFactory
from tests.helpers.solutions import create_github_solution
from tests.helpers.users import create_users
from tests.helpers.workspaces import create_workspace, add_user_to_workspace


@pytest_asyncio.fixture()
def request_grades(client: AsyncClient):
    async def inner(
        workspace_id: int, token: str, task_ids: list[int] | None = None, user_ids: list[int] | None = None
    ) -> Response:
        params = {}
        if task_ids:
            params["task_ids"] = task_ids
        if user_ids:
            params["user_ids"] = user_ids
        return await client.get(
            f"/api/v1/workspaces/{workspace_id}/grades",
            headers={"Authorization": f"Bearer {token}"},
            params=params,
        )

    return inner


@pytest_asyncio.fixture()
def request_grades_csv(client: AsyncClient):
    async def inner(
        workspace_id: int, token: str, task_ids: list[int] | None = None, user_ids: list[int] | None = None
    ) -> Response:
        params = {}
        if task_ids:
            params["task_ids"] = task_ids
        if user_ids:
            params["user_ids"] = user_ids
        return await client.get(
            f"/api/v1/workspaces/{workspace_id}/grades/csv",
            headers={"Authorization": f"Bearer {token}"},
            params=params,
        )

    return inner


@pytest_asyncio.fixture()
def get_grades(request_grades):
    async def inner(
        workspace_id: int, token: str, task_ids: list[int] | None = None, user_ids: list[int] | None = None
    ) -> list[StudentGradesDTO]:
        response = await request_grades(workspace_id, token, task_ids, user_ids)
        assert response.status_code == status.HTTP_200_OK
        return [StudentGradesDTO.model_validate(g) for g in response.json()]

    return inner


@pytest_asyncio.fixture()
def get_grades_csv(request_grades_csv):
    async def inner(
        workspace_id: int, token: str, task_ids: list[int] | None = None, user_ids: list[int] | None = None
    ) -> str:
        response = await request_grades_csv(workspace_id, token, task_ids, user_ids)
        assert response.status_code == status.HTTP_200_OK
        return response.text

    return inner


async def test__success__owner(uow, get_grades):
    owner = (await create_users(uow))[0]
    token = create_access_token(owner.as_short())
    workspace = await create_workspace(uow, owner.id)

    grades = await get_grades(workspace.id, token)
    assert len(grades) == 0


async def test__success__teacher(uow, get_grades):
    owner = (await create_users(uow))[0]
    teacher = (await create_users(uow))[0]
    token = create_access_token(teacher.as_short())
    workspace = await create_workspace(uow, owner.id)
    await add_user_to_workspace(uow, workspace.id, teacher.id, WorkspaceMemberRoleEnum.TEACHER)

    grades = await get_grades(workspace.id, token)
    assert len(grades) == 0


async def test__failed__student_cannot_access(uow, request_grades):
    owner = (await create_users(uow))[0]
    student = (await create_users(uow))[0]
    token = create_access_token(student.as_short())
    workspace = await create_workspace(uow, owner.id)
    await add_user_to_workspace(uow, workspace.id, student.id, WorkspaceMemberRoleEnum.STUDENT)

    response = await request_grades(workspace.id, token)
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json()["code"] == "role_permissions"


async def test__failed__not_member(uow, request_grades):
    owner = (await create_users(uow))[0]
    other_user = (await create_users(uow))[0]
    token = create_access_token(other_user.as_short())
    workspace = await create_workspace(uow, owner.id)

    response = await request_grades(workspace.id, token)
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json()["code"] == "user_not_member"


async def test__failed__unauthorized(request_grades):
    response = await request_grades(1, token="invalid")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


async def test__success__with_tasks_and_grades(uow, get_grades, get_grades_csv):
    owner = (await create_users(uow))[0]
    student = (await create_users(uow))[0]
    token = create_access_token(owner.as_short())
    workspace = await create_workspace(uow, owner.id)
    await add_user_to_workspace(uow, workspace.id, student.id, WorkspaceMemberRoleEnum.STUDENT)

    async with uow.connection():
        task_1 = await uow.tasks.create(TaskFactory.build(workspace_id=workspace.id), owner.id)
        task_2 = await uow.tasks.create(TaskFactory.build(workspace_id=workspace.id), owner.id)

        solution_1 = await create_github_solution(uow, task_1.id, student.id)
        solution_2 = await create_github_solution(uow, task_2.id, student.id)
        solution_3 = await create_github_solution(uow, task_2.id, student.id)

        solution_1 = await uow.solutions.update(solution_1.id, SolutionUpdateDTO(status=SolutionStatusEnum.REVIEWED, human_grade=5))
        solution_2 = await uow.solutions.update(solution_2.id, SolutionUpdateDTO(status=SolutionStatusEnum.REVIEWED, human_grade=8))
        solution_3 =await uow.solutions.update(solution_3.id, SolutionUpdateDTO(status=SolutionStatusEnum.REVIEWED, human_grade=20))


    grades = await get_grades(workspace.id, token)
    assert len(grades) == 2

    with open("txt.tx", "a+") as f:
        f.write(str(grades) + "\n")

    owner_grades = next(g for g in grades if g.user.id == owner.id)
    assert len(owner_grades.tasks) == 2

    student_grades = next(g for g in grades if g.user.id == student.id)
    assert len(student_grades.tasks) == 2

    task_1_grades = next(t for t in student_grades.tasks if t.task_id == task_1.id)
    assert task_1_grades.grade == solution_1.human_grade
    assert task_1_grades.best_solution_id == solution_1.id

    task_2_grades = next(t for t in student_grades.tasks if t.task_id == task_2.id)
    assert task_2_grades.grade == solution_3.human_grade
    assert task_2_grades.best_solution_id == solution_3.id


async def test__success__filter(uow, get_grades):
    owner = (await create_users(uow))[0]
    student = (await create_users(uow))[0]
    token = create_access_token(owner.as_short())
    workspace = await create_workspace(uow, owner.id)
    await add_user_to_workspace(uow, workspace.id, student.id, WorkspaceMemberRoleEnum.STUDENT)

    async with uow.connection():
        task_1 = await uow.tasks.create(TaskFactory.build(workspace_id=workspace.id), owner.id)
        task_2 = await uow.tasks.create(TaskFactory.build(workspace_id=workspace.id), owner.id)

        solution_1 = await create_github_solution(uow, task_1.id, student.id)
        solution_2 = await create_github_solution(uow, task_2.id, student.id)
        await uow.solutions.update(solution_1.id, SolutionUpdateDTO(status=SolutionStatusEnum.REVIEWED, human_grade=5))
        await uow.solutions.update(solution_2.id, SolutionUpdateDTO(status=SolutionStatusEnum.REVIEWED, human_grade=10))

    grades = await get_grades(workspace.id, token, task_ids=[task_1.id], user_ids=[student.id])
    assert len(grades) == 1
    assert len(grades[0].tasks) == 1
    assert grades[0].tasks[0].task_id == task_1.id


async def test__success__csv_empty_workspace(uow, get_grades_csv):
    owner = (await create_users(uow))[0]
    token = create_access_token(owner.as_short())
    workspace = await create_workspace(uow, owner.id)

    csv_content = await get_grades_csv(workspace.id, token)
    assert csv_content == "fullname\n"


async def test__failed__csv_unauthorized(request_grades_csv):
    response = await request_grades_csv(1, token="invalid")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


async def test__success__student_without_solutions(uow, get_grades):
    owner = (await create_users(uow))[0]
    student = (await create_users(uow))[0]
    token = create_access_token(owner.as_short())
    workspace = await create_workspace(uow, owner.id)
    await add_user_to_workspace(uow, workspace.id, student.id, WorkspaceMemberRoleEnum.STUDENT)

    async with uow.connection():
        await uow.tasks.create(TaskFactory.build(workspace_id=workspace.id), owner.id)

    grades = await get_grades(workspace.id, token)
    assert len(grades) == 2

    student_grades = next(g for g in grades if g.user.id == student.id)
    assert len(student_grades.tasks) == 1
    assert student_grades.tasks[0].grade is None
