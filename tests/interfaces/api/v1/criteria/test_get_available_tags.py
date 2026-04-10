from fastapi import status
from httpx import AsyncClient, Response
from pydantic import TypeAdapter
import pytest_asyncio

from src.infrastructure.auth import create_access_token
from tests.helpers.criteria import create_criteria
from tests.helpers.users import create_users


@pytest_asyncio.fixture()
def request_get_available_tags(client: AsyncClient):
    async def inner(token: str) -> Response:
        return await client.get(
            "/api/v1/criteria/available_tags",
            headers={"Authorization": f"Bearer {token}"},
        )

    return inner


@pytest_asyncio.fixture()
def get_available_tags(request_get_available_tags):
    async def inner(token: str) -> list[str]:
        response = await request_get_available_tags(token)
        assert response.status_code == status.HTTP_200_OK
        return TypeAdapter(list[str]).validate_json(response.text)

    return inner


async def test__success__returns_tags(uow, get_available_tags):
    user = (await create_users(uow))[0]
    token = create_access_token(user.as_short())

    await create_criteria(uow, user.id, tags=["python", "api"], is_public=True)
    await create_criteria(uow, user.id, tags=["fastapi"], is_public=True)

    tags = await get_available_tags(token)
    assert "python" in tags
    assert "api" in tags
    assert "fastapi" in tags


async def test__success__excludes_other_users_private_tags(uow, get_available_tags):
    user = (await create_users(uow))[0]
    other_user = (await create_users(uow))[0]
    token = create_access_token(user.as_short())

    await create_criteria(uow, other_user.id, tags=["other_private", "other_public"], is_public=False, size=1)
    await create_criteria(uow, other_user.id, tags=["other_public"], is_public=True, size=1)

    tags = await get_available_tags(token)
    assert "other_private" not in tags
    assert "other_public" in tags


async def test__failed__unauthorized(request_get_available_tags):
    response = await request_get_available_tags(token="invalid")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
