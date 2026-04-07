from fastapi import status
from httpx import AsyncClient, Response
import pytest_asyncio

from src.constants.workspaces import WorkspaceMemberRoleEnum
from src.dto.workspaces.member import WorkspaceMemberFiltersDTO
from src.infrastructure.auth import create_access_token
from tests.helpers.users import create_users
from tests.helpers.workspaces import create_workspace, add_user_to_workspace


@pytest_asyncio.fixture()
def request_leave_workspace(client: AsyncClient):
    async def inner(workspace_id: int, token: str) -> Response:
        return await client.post(
            f"/api/v1/workspaces/{workspace_id}/leave",
            headers={"Authorization": f"Bearer {token}"},
        )

    return inner


async def test__success__student(uow, request_leave_workspace):
    owner = (await create_users(uow))[0]
    student = (await create_users(uow))[0]
    token = create_access_token(student.as_short())
    workspace = await create_workspace(uow, owner.id)
    await add_user_to_workspace(uow, workspace.id, student.id, WorkspaceMemberRoleEnum.STUDENT)

    response = await request_leave_workspace(workspace.id, token)
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["message"] == "Пользователь покинул пространство"

    async with uow.connection():
        members = await uow.workspace_members.get_list(WorkspaceMemberFiltersDTO(workspace_id=workspace.id))
        student_members = [m for m in members if m.user_id == student.id]
        assert len(student_members) == 0


async def test__success__teacher(uow, request_leave_workspace):
    owner = (await create_users(uow))[0]
    teacher = (await create_users(uow))[0]
    token = create_access_token(teacher.as_short())
    workspace = await create_workspace(uow, owner.id)
    await add_user_to_workspace(uow, workspace.id, teacher.id, WorkspaceMemberRoleEnum.TEACHER)

    response = await request_leave_workspace(workspace.id, token)
    assert response.status_code == status.HTTP_200_OK


async def test__failed__owner_cannot_leave(uow, request_leave_workspace):
    owner = (await create_users(uow))[0]
    token = create_access_token(owner.as_short())
    workspace = await create_workspace(uow, owner.id)

    response = await request_leave_workspace(workspace.id, token)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["code"] == "owner_cannot_leave"


async def test__failed__not_member(uow, request_leave_workspace):
    owner = (await create_users(uow))[0]
    workspace = await create_workspace(uow, owner.id)
    other_user = (await create_users(uow))[0]
    token = create_access_token(other_user.as_short())

    response = await request_leave_workspace(workspace.id, token)
    assert response.status_code == status.HTTP_404_NOT_FOUND


async def test__failed__workspace_not_found(uow, request_leave_workspace):
    user = (await create_users(uow))[0]
    token = create_access_token(user.as_short())

    response = await request_leave_workspace(9999, token)
    assert response.status_code == status.HTTP_404_NOT_FOUND


async def test__failed__unauthorized(request_leave_workspace):
    response = await request_leave_workspace(1, token="invalid")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
