from fastapi import status
from httpx import AsyncClient, Response
import pytest_asyncio

from src.constants.workspaces import WorkspaceMemberRoleEnum
from src.dto.workspaces.join_rule import WorkspaceJoinRuleRequestUpdateDTO, WorkspaceJoinRuleFullDTO, \
    WorkspaceJoinRuleResponseDTO
from src.infrastructure.auth import create_access_token
from tests.helpers.users import create_users
from tests.helpers.workspaces import create_workspace, add_user_to_workspace, create_join_rule


@pytest_asyncio.fixture()
def request_update_join_rule(client: AsyncClient):
    async def inner(workspace_id: int, rule_id: int, data: WorkspaceJoinRuleRequestUpdateDTO, token: str) -> Response:
        return await client.put(
            f"/api/v1/workspaces/{workspace_id}/join_rules/{rule_id}",
            json=data.model_dump(by_alias=True),
            headers={"Authorization": f"Bearer {token}"},
        )

    return inner


@pytest_asyncio.fixture()
def update_join_rule(request_update_join_rule):
    async def inner(
        workspace_id: int, rule_id: int, data: WorkspaceJoinRuleRequestUpdateDTO, token: str
    ) -> WorkspaceJoinRuleResponseDTO:
        response = await request_update_join_rule(workspace_id, rule_id, data, token)
        assert response.status_code == status.HTTP_200_OK
        return WorkspaceJoinRuleResponseDTO.model_validate_json(response.text)

    return inner


async def test__success__owner(uow, update_join_rule):
    owner = (await create_users(uow))[0]
    token = create_access_token(owner.as_short())
    workspace = await create_workspace(uow, owner.id)
    await create_join_rule(uow, workspace.id, slug="test-slug-update")

    async with uow.connection():
        rules = await uow.workspace_join_rules.get_list(workspace.id)
        rule_id = rules[0].id

    data = WorkspaceJoinRuleRequestUpdateDTO(slug="updated-slug", role=WorkspaceMemberRoleEnum.TEACHER)
    result = await update_join_rule(workspace.id, rule_id, data, token)
    assert result.slug == "updated-slug"
    assert result.role == WorkspaceMemberRoleEnum.TEACHER


async def test__success__teacher(uow, update_join_rule):
    owner = (await create_users(uow))[0]
    teacher = (await create_users(uow))[0]
    token = create_access_token(teacher.as_short())
    workspace = await create_workspace(uow, owner.id)
    await add_user_to_workspace(uow, workspace.id, teacher.id, WorkspaceMemberRoleEnum.TEACHER)
    await create_join_rule(uow, workspace.id, slug="test-slug-teacher")

    async with uow.connection():
        rules = await uow.workspace_join_rules.get_list(workspace.id)
        rule_id = rules[0].id

    data = WorkspaceJoinRuleRequestUpdateDTO(slug="teacher-updated", role=WorkspaceMemberRoleEnum.STUDENT)
    result = await update_join_rule(workspace.id, rule_id, data, token)
    assert result.slug == "teacher-updated"


async def test__failed__student(uow, request_update_join_rule):
    owner = (await create_users(uow))[0]
    student = (await create_users(uow))[0]
    token = create_access_token(student.as_short())
    workspace = await create_workspace(uow, owner.id)
    await add_user_to_workspace(uow, workspace.id, student.id, WorkspaceMemberRoleEnum.STUDENT)
    await create_join_rule(uow, workspace.id, slug="test-slug-student")

    async with uow.connection():
        rules = await uow.workspace_join_rules.get_list(workspace.id)
        rule_id = rules[0].id

    data = WorkspaceJoinRuleRequestUpdateDTO(slug="updated", role=WorkspaceMemberRoleEnum.STUDENT)
    response = await request_update_join_rule(workspace.id, rule_id, data, token)
    assert response.status_code == status.HTTP_403_FORBIDDEN


async def test__failed__owner_role_not_allowed(uow, request_update_join_rule):
    owner = (await create_users(uow))[0]
    token = create_access_token(owner.as_short())
    workspace = await create_workspace(uow, owner.id)
    await create_join_rule(uow, workspace.id, slug="test-slug-owner")

    async with uow.connection():
        rules = await uow.workspace_join_rules.get_list(workspace.id)
        rule_id = rules[0].id

    data = WorkspaceJoinRuleRequestUpdateDTO(slug="updated", role=WorkspaceMemberRoleEnum.OWNER)
    response = await request_update_join_rule(workspace.id, rule_id, data, token)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["code"] == "not_available__join_rule_role"


async def test__failed__unauthorized(request_update_join_rule):
    data = WorkspaceJoinRuleRequestUpdateDTO(slug="updated", role=WorkspaceMemberRoleEnum.STUDENT)
    response = await request_update_join_rule(1, 1, data, token="invalid")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
