from fastapi import status
from httpx import AsyncClient, Response
import pytest_asyncio

from src.dto.workspaces import JoinBySlugDTO, JoinResponseDTO
from src.infrastructure.auth import create_access_token
from tests.helpers.users import create_users
from tests.helpers.workspaces import create_join_rule, create_workspace


@pytest_asyncio.fixture()
def request_join_by_slug(client: AsyncClient):
    async def inner(data: JoinBySlugDTO, token: str) -> Response:
        return await client.post(
            "/api/v1/joins",
            json=data.model_dump(by_alias=True),
            headers={"Authorization": f"Bearer {token}"},
        )

    return inner


@pytest_asyncio.fixture()
def join_by_slug(request_join_by_slug):
    async def inner(data: JoinBySlugDTO, token: str) -> JoinResponseDTO:
        response = await request_join_by_slug(data, token)
        assert response.status_code == status.HTTP_200_OK
        return JoinResponseDTO.model_validate_json(response.text)

    return inner


async def test__success(uow, join_by_slug):
    owner = (await create_users(uow))[0]
    workspace = await create_workspace(uow, owner.id)

    await create_join_rule(uow, workspace.id, slug="test-slug")

    other_user = (await create_users(uow))[0]
    token = create_access_token(other_user.as_short())

    data = JoinBySlugDTO(slug="test-slug")
    result = await join_by_slug(data, token)

    assert result.workspace_id == workspace.id


async def test__failed__invalid_slug(uow, request_join_by_slug):
    owner = (await create_users(uow))[0]
    workspace = await create_workspace(uow, owner.id)

    await create_join_rule(uow, workspace.id, slug="existing-slug")

    user = (await create_users(uow))[0]
    token = create_access_token(user.as_short())

    data = JoinBySlugDTO(slug="non-existent-slug")
    response = await request_join_by_slug(data, token)

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["code"] == "not_found"


async def test__failed__already_member(uow, request_join_by_slug):
    owner = (await create_users(uow))[0]
    workspace = await create_workspace(uow, owner.id)

    await create_join_rule(uow, workspace.id, slug="test-slug")

    token = create_access_token(owner.as_short())

    data = JoinBySlugDTO(slug="test-slug")
    response = await request_join_by_slug(data, token)

    assert response.status_code == status.HTTP_409_CONFLICT
    assert response.json()["code"] == "already_member"


async def test__failed__unauthorized(request_join_by_slug):
    data = JoinBySlugDTO(slug="test-slug")
    response = await request_join_by_slug(data, token="invalid")

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
