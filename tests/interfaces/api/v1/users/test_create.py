from fastapi import status
from httpx import AsyncClient, Response
import pytest_asyncio

from src.dto.users import UserCreateDTO, UserResponseDTO
from tests.factories.users import UserFactory
from tests.helpers.users import create_users


@pytest_asyncio.fixture()
def request_create_user(client: AsyncClient):
    async def inner(data: UserCreateDTO) -> Response:
        return await client.post("/api/v1/users", json=data.model_dump(by_alias=True))

    return inner


@pytest_asyncio.fixture()
def create_user(request_create_user):
    async def inner(data: UserCreateDTO) -> UserResponseDTO:
        response = await request_create_user(data)
        assert response.status_code == status.HTTP_200_OK
        return UserResponseDTO.model_validate_json(response.text)

    return inner


async def test__success(container, create_user):
    data: UserCreateDTO = UserFactory.build()

    user = await create_user(data)
    assert user.email == data.email
    assert user.fullname == data.fullname
    assert not user.is_admin


async def test__failed__duplicated_email(uow, request_create_user):
    created_user = (await create_users(uow))[0]
    data: UserCreateDTO = UserFactory.build(email=created_user.email)

    response = await request_create_user(data)
    assert response.status_code == status.HTTP_409_CONFLICT
    assert response.json()["code"] == "user_email_exists"
