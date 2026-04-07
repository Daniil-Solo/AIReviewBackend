from fastapi import status
from httpx import AsyncClient, Response
import pytest_asyncio

from src.constants.workspaces import WorkspaceMemberRoleEnum
from src.dto.workspaces.workspace import WorkspaceUpdateDTO, WorkspaceResponseDTO
from src.infrastructure.auth import create_access_token
from tests.factories.workspaces import WorkspaceFactory
from tests.helpers.users import create_users
from tests.helpers.workspaces import create_workspace, add_user_to_workspace


@pytest_asyncio.fixture()
def request_update_workspace(client: AsyncClient):
    async def inner(workspace_id: int, data: WorkspaceUpdateDTO, token: str) -> Response:
        return await client.put(
            f"/api/v1/workspaces/{workspace_id}",
            json=data.model_dump(by_alias=True),
            headers={"Authorization": f"Bearer {token}"},
        )

    return inner


@pytest_asyncio.fixture()
def update_workspace(request_update_workspace):
    async def inner(workspace_id: int, data: WorkspaceUpdateDTO, token: str) -> WorkspaceResponseDTO:
        response = await request_update_workspace(workspace_id, data, token)
        assert response.status_code == status.HTTP_200_OK
        return WorkspaceResponseDTO.model_validate_json(response.text)

    return inner


async def test__success__owner(uow, update_workspace):
    user = (await create_users(uow))[0]
    token = create_access_token(user.as_short())
    workspace = await create_workspace(uow, user.id)
    data = WorkspaceUpdateDTO(name="Updated Name", description="Updated Description")

    result = await update_workspace(workspace.id, data, token)
    assert result.name == "Updated Name"
    assert result.description == "Updated Description"


async def test__success__teacher(uow, update_workspace):
    owner = (await create_users(uow))[0]
    teacher = (await create_users(uow))[0]
    token = create_access_token(teacher.as_short())
    workspace = await create_workspace(uow, owner.id)
    await add_user_to_workspace(uow, workspace.id, teacher.id, WorkspaceMemberRoleEnum.TEACHER)
    data = WorkspaceUpdateDTO(name="Updated by Teacher", description="Updated")

    result = await update_workspace(workspace.id, data, token)
    assert result.name == "Updated by Teacher"


async def test__failed__student(uow, request_update_workspace):
    owner = (await create_users(uow))[0]
    student = (await create_users(uow))[0]
    token = create_access_token(student.as_short())
    workspace = await create_workspace(uow, owner.id)
    await add_user_to_workspace(uow, workspace.id, student.id, WorkspaceMemberRoleEnum.STUDENT)
    data = WorkspaceUpdateDTO(name="Updated", description="")

    response = await request_update_workspace(workspace.id, data, token)
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json()["code"] == "role_permissions"


async def test__failed__not_member(uow, request_update_workspace):
    user = (await create_users(uow))[0]
    other_user = (await create_users(uow))[0]
    token = create_access_token(other_user.as_short())
    workspace = await create_workspace(uow, user.id)
    data = WorkspaceUpdateDTO(name="Updated", description="")

    response = await request_update_workspace(workspace.id, data, token)
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json()["code"] == "user_not_member"


async def test__failed__unauthorized(request_update_workspace):
    data = WorkspaceUpdateDTO(name="Updated", description="")
    response = await request_update_workspace(1, data, token="invalid")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
