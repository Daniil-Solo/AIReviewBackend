from fastapi import status
from httpx import AsyncClient, Response
import pytest_asyncio

from src.constants.workspaces import WorkspaceMemberRoleEnum
from src.infrastructure.auth import create_access_token
from tests.helpers.users import create_users
from tests.helpers.workspaces import create_workspace, add_user_to_workspace


@pytest_asyncio.fixture()
def request_archive_workspace(client: AsyncClient):
    async def inner(workspace_id: int, token: str) -> Response:
        return await client.delete(
            f"/api/v1/workspaces/{workspace_id}",
            headers={"Authorization": f"Bearer {token}"},
        )

    return inner


async def test__success(uow, request_archive_workspace):
    user = (await create_users(uow))[0]
    token = create_access_token(user.as_short())
    workspace = await create_workspace(uow, user.id)

    response = await request_archive_workspace(workspace.id, token)
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["message"] == "Пространство архивировано"

    async with uow.connection():
        archived_workspace = await uow.workspaces.get_by_id(workspace.id)
        assert archived_workspace.is_archived


async def test__failed__teacher(uow, request_archive_workspace):
    owner = (await create_users(uow))[0]
    teacher = (await create_users(uow))[0]
    token = create_access_token(teacher.as_short())
    workspace = await create_workspace(uow, owner.id)
    await add_user_to_workspace(uow, workspace.id, teacher.id, WorkspaceMemberRoleEnum.TEACHER)

    response = await request_archive_workspace(workspace.id, token)
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json()["code"] == "role_permissions"


async def test__failed__student(uow, request_archive_workspace):
    owner = (await create_users(uow))[0]
    student = (await create_users(uow))[0]
    token = create_access_token(student.as_short())
    workspace = await create_workspace(uow, owner.id)
    await add_user_to_workspace(uow, workspace.id, student.id, WorkspaceMemberRoleEnum.STUDENT)

    response = await request_archive_workspace(workspace.id, token)
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json()["code"] == "role_permissions"


async def test__failed__not_member(uow, request_archive_workspace):
    user = (await create_users(uow))[0]
    other_user = (await create_users(uow))[0]
    token = create_access_token(other_user.as_short())
    workspace = await create_workspace(uow, user.id)

    response = await request_archive_workspace(workspace.id, token)
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json()["code"] == "user_not_member"


async def test__failed__workspace_not_found(uow, request_archive_workspace):
    user = (await create_users(uow))[0]
    token = create_access_token(user.as_short())

    response = await request_archive_workspace(9999, token)
    assert response.status_code == status.HTTP_404_NOT_FOUND


async def test__failed__unauthorized(request_archive_workspace):
    response = await request_archive_workspace(1, token="invalid")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
