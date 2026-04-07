from fastapi import status
from httpx import AsyncClient, Response
import pytest_asyncio

from src.constants.workspaces import WorkspaceMemberRoleEnum
from src.infrastructure.auth import create_access_token
from tests.helpers.users import create_users
from tests.helpers.workspaces import create_workspace, add_user_to_workspace, create_join_rule


@pytest_asyncio.fixture()
def request_delete_join_rule(client: AsyncClient):
    async def inner(workspace_id: int, rule_id: int, token: str) -> Response:
        return await client.delete(
            f"/api/v1/workspaces/{workspace_id}/join_rules/{rule_id}",
            headers={"Authorization": f"Bearer {token}"},
        )

    return inner


async def test__success__owner(uow, request_delete_join_rule):
    owner = (await create_users(uow))[0]
    token = create_access_token(owner.as_short())
    workspace = await create_workspace(uow, owner.id)
    await create_join_rule(uow, workspace.id, slug="test-slug-delete")

    async with uow.connection():
        rules = await uow.workspace_join_rules.get_list(workspace.id)
        rule_id = rules[0].id

    response = await request_delete_join_rule(workspace.id, rule_id, token)
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["message"] == "Правило приглашения удалено"

    async with uow.connection():
        rules = await uow.workspace_join_rules.get_list(workspace.id)
        assert len(rules) == 0


async def test__success__teacher(uow, request_delete_join_rule):
    owner = (await create_users(uow))[0]
    teacher = (await create_users(uow))[0]
    token = create_access_token(teacher.as_short())
    workspace = await create_workspace(uow, owner.id)
    await add_user_to_workspace(uow, workspace.id, teacher.id, WorkspaceMemberRoleEnum.TEACHER)
    await create_join_rule(uow, workspace.id, slug="test-slug-teacher-delete")

    async with uow.connection():
        rules = await uow.workspace_join_rules.get_list(workspace.id)
        rule_id = rules[0].id

    response = await request_delete_join_rule(workspace.id, rule_id, token)
    assert response.status_code == status.HTTP_200_OK


async def test__failed__student(uow, request_delete_join_rule):
    owner = (await create_users(uow))[0]
    student = (await create_users(uow))[0]
    token = create_access_token(student.as_short())
    workspace = await create_workspace(uow, owner.id)
    await add_user_to_workspace(uow, workspace.id, student.id, WorkspaceMemberRoleEnum.STUDENT)
    await create_join_rule(uow, workspace.id, slug="test-slug-student-delete")

    async with uow.connection():
        rules = await uow.workspace_join_rules.get_list(workspace.id)
        rule_id = rules[0].id

    response = await request_delete_join_rule(workspace.id, rule_id, token)
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json()["code"] == "role_permissions"


async def test__failed__not_member(uow, request_delete_join_rule):
    user = (await create_users(uow))[0]
    other_user = (await create_users(uow))[0]
    token = create_access_token(other_user.as_short())
    workspace = await create_workspace(uow, user.id)
    await create_join_rule(uow, workspace.id, slug="test-slug-not-member")

    async with uow.connection():
        rules = await uow.workspace_join_rules.get_list(workspace.id)
        rule_id = rules[0].id

    response = await request_delete_join_rule(workspace.id, rule_id, token)
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json()["code"] == "user_not_member"


async def test__failed__rule_not_found(uow, request_delete_join_rule):
    owner = (await create_users(uow))[0]
    token = create_access_token(owner.as_short())
    workspace = await create_workspace(uow, owner.id)

    response = await request_delete_join_rule(workspace.id, 9999, token)
    assert response.status_code == status.HTTP_404_NOT_FOUND


async def test__failed__unauthorized(request_delete_join_rule):
    response = await request_delete_join_rule(1, 1, token="invalid")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
