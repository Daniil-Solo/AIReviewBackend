from fastapi import status
from httpx import AsyncClient, Response
from pydantic import TypeAdapter
import pytest_asyncio

from src.dto.users import UserResponseDTO
from src.infrastructure.auth import create_access_token
from tests.helpers.users import create_users


@pytest_asyncio.fixture()
def request_get_users(client: AsyncClient):
    async def inner(token: str) -> Response:
        return await client.get("/api/v1/users", headers={"Authorization": f"Bearer {token}"})

    return inner


@pytest_asyncio.fixture()
def get_users(request_get_users):
    async def inner(token: str) -> list[UserResponseDTO]:
        response = await request_get_users(token)
        assert response.status_code == status.HTTP_200_OK
        return TypeAdapter(list[UserResponseDTO]).validate_json(response.text)

    return inner


async def test__success(uow, get_users):
    admin = (await create_users(uow, is_admin=True))[0]
    admin_token = create_access_token(admin.as_short())
    other_users = await create_users(uow, size=5)

    users = await get_users(admin_token)
    assert len(users) == len([admin, *other_users])


async def test__failed__not_admin(uow, request_get_users):
    user = (await create_users(uow))[0]
    user_token = create_access_token(user.as_short())
    await create_users(uow, size=5)

    response = await request_get_users(user_token)
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json()["code"] == "admin_only"
