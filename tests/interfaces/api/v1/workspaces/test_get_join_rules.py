from fastapi import status
from httpx import AsyncClient, Response
import pytest_asyncio

from src.constants.workspaces import WorkspaceMemberRoleEnum
from src.dto.workspaces.join_rule import WorkspaceJoinRuleFullDTO, WorkspaceJoinRuleResponseDTO
from src.infrastructure.auth import create_access_token
from tests.helpers.users import create_users
from tests.helpers.workspaces import create_workspace, add_user_to_workspace, create_join_rule


@pytest_asyncio.fixture()
def request_get_join_rules(client: AsyncClient):
    async def inner(workspace_id: int, token: str) -> Response:
        return await client.get(
            f"/api/v1/workspaces/{workspace_id}/join_rules",
            headers={"Authorization": f"Bearer {token}"},
        )

    return inner


@pytest_asyncio.fixture()
def get_join_rules(request_get_join_rules):
    async def inner(workspace_id: int, token: str) -> list[WorkspaceJoinRuleResponseDTO]:
        response = await request_get_join_rules(workspace_id, token)
        assert response.status_code == status.HTTP_200_OK
        return [WorkspaceJoinRuleResponseDTO.model_validate(r) for r in response.json()]

    return inner


async def test__success__owner(uow, get_join_rules):
    owner = (await create_users(uow))[0]
    token = create_access_token(owner.as_short())
    workspace = await create_workspace(uow, owner.id)
    await create_join_rule(uow, workspace.id, slug="test-slug-1")

    rules = await get_join_rules(workspace.id, token)
    assert len(rules) == 1
    assert rules[0].slug == "test-slug-1"


async def test__success__teacher(uow, get_join_rules):
    owner = (await create_users(uow))[0]
    teacher = (await create_users(uow))[0]
    token = create_access_token(teacher.as_short())
    workspace = await create_workspace(uow, owner.id)
    await add_user_to_workspace(uow, workspace.id, teacher.id, WorkspaceMemberRoleEnum.TEACHER)
    await create_join_rule(uow, workspace.id, slug="test-slug-2")

    rules = await get_join_rules(workspace.id, token)
    assert len(rules) == 1


async def test__failed__student(uow, request_get_join_rules):
    owner = (await create_users(uow))[0]
    student = (await create_users(uow))[0]
    token = create_access_token(student.as_short())
    workspace = await create_workspace(uow, owner.id)
    await add_user_to_workspace(uow, workspace.id, student.id, WorkspaceMemberRoleEnum.STUDENT)

    response = await request_get_join_rules(workspace.id, token)
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json()["code"] == "role_permissions"


async def test__failed__not_member(uow, request_get_join_rules):
    user = (await create_users(uow))[0]
    other_user = (await create_users(uow))[0]
    token = create_access_token(other_user.as_short())
    workspace = await create_workspace(uow, user.id)

    response = await request_get_join_rules(workspace.id, token)
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json()["code"] == "user_not_member"


async def test__failed__unauthorized(request_get_join_rules):
    response = await request_get_join_rules(1, token="invalid")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
