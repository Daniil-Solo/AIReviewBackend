from fastapi import status
from httpx import AsyncClient, Response
import pytest_asyncio

from src.constants.workspaces import WorkspaceMemberRoleEnum
from src.dto.workspaces.join_rule import WorkspaceJoinRuleRequestCreateDTO, WorkspaceJoinRuleFullDTO, \
    WorkspaceJoinRuleResponseDTO
from src.infrastructure.auth import create_access_token
from tests.factories.workspaces import WorkspaceJoinRuleFactory
from tests.helpers.users import create_users
from tests.helpers.workspaces import create_workspace, add_user_to_workspace


@pytest_asyncio.fixture()
def request_create_join_rule(client: AsyncClient):
    async def inner(workspace_id: int, data: WorkspaceJoinRuleRequestCreateDTO, token: str) -> Response:
        return await client.post(
            f"/api/v1/workspaces/{workspace_id}/join_rules",
            json=data.model_dump(by_alias=True),
            headers={"Authorization": f"Bearer {token}"},
        )

    return inner


@pytest_asyncio.fixture()
def create_join_rule(request_create_join_rule):
    async def inner(
        workspace_id: int, data: WorkspaceJoinRuleRequestCreateDTO, token: str
    ) -> WorkspaceJoinRuleResponseDTO:
        response = await request_create_join_rule(workspace_id, data, token)
        assert response.status_code == status.HTTP_200_OK
        return WorkspaceJoinRuleResponseDTO.model_validate_json(response.text)

    return inner


async def test__success__owner(uow, create_join_rule):
    owner = (await create_users(uow))[0]
    token = create_access_token(owner.as_short())
    workspace = await create_workspace(uow, owner.id)
    data = WorkspaceJoinRuleFactory.build()

    result = await create_join_rule(workspace.id, data, token)
    assert result.slug == data.slug
    assert result.role == data.role
    assert result.is_active


async def test__success__teacher(uow, create_join_rule):
    owner = (await create_users(uow))[0]
    teacher = (await create_users(uow))[0]
    token = create_access_token(teacher.as_short())
    workspace = await create_workspace(uow, owner.id)
    await add_user_to_workspace(uow, workspace.id, teacher.id, WorkspaceMemberRoleEnum.TEACHER)
    data = WorkspaceJoinRuleFactory.build()

    result = await create_join_rule(workspace.id, data, token)
    assert result.slug == data.slug


async def test__success__with_password(uow, create_join_rule):
    owner = (await create_users(uow))[0]
    token = create_access_token(owner.as_short())
    workspace = await create_workspace(uow, owner.id)
    data = WorkspaceJoinRuleRequestCreateDTO(
        slug="test-slug", role=WorkspaceMemberRoleEnum.STUDENT, password="secret123"
    )

    result = await create_join_rule(workspace.id, data, token)
    assert result.slug == "test-slug"


async def test__failed__student(uow, request_create_join_rule):
    owner = (await create_users(uow))[0]
    student = (await create_users(uow))[0]
    token = create_access_token(student.as_short())
    workspace = await create_workspace(uow, owner.id)
    await add_user_to_workspace(uow, workspace.id, student.id, WorkspaceMemberRoleEnum.STUDENT)
    data = WorkspaceJoinRuleFactory.build()

    response = await request_create_join_rule(workspace.id, data, token)
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json()["code"] == "role_permissions"


async def test__failed__owner_role_not_allowed(uow, request_create_join_rule):
    owner = (await create_users(uow))[0]
    token = create_access_token(owner.as_short())
    workspace = await create_workspace(uow, owner.id)
    data = WorkspaceJoinRuleRequestCreateDTO(slug="test-slug", role=WorkspaceMemberRoleEnum.OWNER)

    response = await request_create_join_rule(workspace.id, data, token)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["code"] == "not_available__join_rule_role"


async def test__failed__not_member(uow, request_create_join_rule):
    user = (await create_users(uow))[0]
    other_user = (await create_users(uow))[0]
    token = create_access_token(other_user.as_short())
    workspace = await create_workspace(uow, user.id)
    data = WorkspaceJoinRuleFactory.build()

    response = await request_create_join_rule(workspace.id, data, token)
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json()["code"] == "user_not_member"


async def test__failed__unauthorized(request_create_join_rule):
    data = WorkspaceJoinRuleFactory.build()
    response = await request_create_join_rule(1, data, token="invalid")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
