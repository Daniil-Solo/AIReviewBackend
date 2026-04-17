from fastapi import status
from httpx import AsyncClient, Response
import pytest_asyncio

from src.dto.workspaces.join import SlugCheckResponseDTO
from tests.helpers.users import create_users
from tests.helpers.workspaces import create_workspace, create_join_rule


@pytest_asyncio.fixture()
def request_check_slug(client: AsyncClient):
    async def inner(slug: str) -> Response:
        return await client.get(f"/api/v1/workspaces/slugs/availability?slug={slug}")

    return inner


@pytest_asyncio.fixture()
def check_slug(request_check_slug):
    async def inner(slug: str) -> SlugCheckResponseDTO:
        response = await request_check_slug(slug)
        assert response.status_code == status.HTTP_200_OK
        return SlugCheckResponseDTO.model_validate_json(response.text)

    return inner


async def test__success__available_slug(uow, check_slug):
    result = await check_slug("new-unique-slug-123")
    assert result.slug == "new-unique-slug-123"
    assert result.is_available


async def test__success__taken_slug(uow, check_slug):
    owner = (await create_users(uow))[0]
    workspace = await create_workspace(uow, owner.id)
    await create_join_rule(uow, workspace.id, slug="existing-slug")

    result = await check_slug("existing-slug")
    assert result.slug == "existing-slug"
    assert not result.is_available


