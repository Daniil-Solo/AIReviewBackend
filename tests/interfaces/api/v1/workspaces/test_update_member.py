from fastapi import status
from httpx import AsyncClient, Response
import pytest_asyncio

from src.constants.workspaces import WorkspaceMemberRoleEnum
from src.dto.workspaces.member import WorkspaceMemberUpdateDTO, WorkspaceMemberResponseDTO, WorkspaceMemberFiltersDTO
from src.infrastructure.auth import create_access_token
from tests.helpers.users import create_users
from tests.helpers.workspaces import create_workspace, add_user_to_workspace


@pytest_asyncio.fixture()
def request_update_member(client: AsyncClient):
    async def inner(workspace_id: int, member_id: int, data: WorkspaceMemberUpdateDTO, token: str) -> Response:
        return await client.patch(
            f"/api/v1/workspaces/{workspace_id}/members/{member_id}",
            json=data.model_dump(by_alias=True),
            headers={"Authorization": f"Bearer {token}"},
        )

    return inner


@pytest_asyncio.fixture()
def update_member(request_update_member):
    async def inner(
        workspace_id: int, member_id: int, data: WorkspaceMemberUpdateDTO, token: str
    ) -> WorkspaceMemberResponseDTO:
        response = await request_update_member(workspace_id, member_id, data, token)
        assert response.status_code == status.HTTP_200_OK
        return WorkspaceMemberResponseDTO.model_validate_json(response.text)

    return inner


async def test__success__owner_updates_student(uow, update_member):
    owner = (await create_users(uow))[0]
    student = (await create_users(uow))[0]
    token = create_access_token(owner.as_short())
    workspace = await create_workspace(uow, owner.id)
    await add_user_to_workspace(uow, workspace.id, student.id, WorkspaceMemberRoleEnum.STUDENT)

    async with uow.connection():
        members = await uow.workspace_members.get_list(WorkspaceMemberFiltersDTO(workspace_id=workspace.id))
        student_member = [m for m in members if m.user_id == student.id][0]

    data = WorkspaceMemberUpdateDTO(role=WorkspaceMemberRoleEnum.TEACHER)
    result = await update_member(workspace.id, student_member.id, data, token)
    assert result.role == WorkspaceMemberRoleEnum.TEACHER


async def test__failed__teacher_cannot_update(uow, request_update_member):
    owner = (await create_users(uow))[0]
    teacher = (await create_users(uow))[0]
    student = (await create_users(uow))[0]
    token = create_access_token(teacher.as_short())
    workspace = await create_workspace(uow, owner.id)
    await add_user_to_workspace(uow, workspace.id, teacher.id, WorkspaceMemberRoleEnum.TEACHER)
    await add_user_to_workspace(uow, workspace.id, student.id, WorkspaceMemberRoleEnum.STUDENT)

    async with uow.connection():
        members = await uow.workspace_members.get_list(WorkspaceMemberFiltersDTO(workspace_id=workspace.id))
        student_member = [m for m in members if m.user_id == student.id][0]

    data = WorkspaceMemberUpdateDTO(role=WorkspaceMemberRoleEnum.TEACHER)
    response = await request_update_member(workspace.id, student_member.id, data, token)
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json()["code"] == "role_permissions"


async def test__failed__cannot_update_owner_role(uow, request_update_member):
    owner = (await create_users(uow))[0]
    token = create_access_token(owner.as_short())
    workspace = await create_workspace(uow, owner.id)

    async with uow.connection():
        members = await uow.workspace_members.get_list(WorkspaceMemberFiltersDTO(workspace_id=workspace.id))
        owner_member = [m for m in members if m.user_id == owner.id][0]

    data = WorkspaceMemberUpdateDTO(role=WorkspaceMemberRoleEnum.TEACHER)
    response = await request_update_member(workspace.id, owner_member.id, data, token)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["code"] == "cannot_change_owner_role"


async def test__failed__cannot_set_owner_role(uow, request_update_member):
    owner = (await create_users(uow))[0]
    student = (await create_users(uow))[0]
    token = create_access_token(owner.as_short())
    workspace = await create_workspace(uow, owner.id)
    await add_user_to_workspace(uow, workspace.id, student.id, WorkspaceMemberRoleEnum.STUDENT)

    async with uow.connection():
        members = await uow.workspace_members.get_list(WorkspaceMemberFiltersDTO(workspace_id=workspace.id))
        student_member = [m for m in members if m.user_id == student.id][0]

    data = WorkspaceMemberUpdateDTO(role=WorkspaceMemberRoleEnum.OWNER)
    response = await request_update_member(workspace.id, student_member.id, data, token)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["code"] == "owner_not_available"


async def test__failed__member_not_in_workspace(uow, request_update_member):
    owner = (await create_users(uow))[0]
    token = create_access_token(owner.as_short())
    workspace = await create_workspace(uow, owner.id)
    data = WorkspaceMemberUpdateDTO(role=WorkspaceMemberRoleEnum.TEACHER)

    response = await request_update_member(workspace.id, 9999, data, token)
    assert response.status_code == status.HTTP_404_NOT_FOUND


async def test__failed__unauthorized(request_update_member):
    data = WorkspaceMemberUpdateDTO(role=WorkspaceMemberRoleEnum.TEACHER)
    response = await request_update_member(1, 1, data, token="invalid")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
