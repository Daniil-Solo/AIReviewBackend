from fastapi import status
from httpx import AsyncClient, Response
import pytest_asyncio

from src.dto.transactions.transactions import AdminTopUpDTO, TransactionResponseDTO
from src.infrastructure.auth import create_access_token
from tests.factories.transactions import TransactionFactory
from tests.helpers.users import create_users


@pytest_asyncio.fixture()
def request_create_transaction(client: AsyncClient):
    async def inner(data: AdminTopUpDTO, token: str) -> Response:
        return await client.post(
            "/api/v1/transactions",
            json=data.model_dump(by_alias=True),
            headers={"Authorization": f"Bearer {token}"},
        )

    return inner


@pytest_asyncio.fixture()
def create_transaction(request_create_transaction):
    async def inner(data: AdminTopUpDTO, token: str) -> TransactionResponseDTO:
        response = await request_create_transaction(data, token)
        assert response.status_code == status.HTTP_200_OK
        return TransactionResponseDTO.model_validate_json(response.text)

    return inner


async def test__success__admin(uow, create_transaction):
    admin = (await create_users(uow, is_admin=True))[0]
    target_user = (await create_users(uow))[0]
    token = create_access_token(admin.as_short())
    data = TransactionFactory.build(user_id=target_user.id, amount=5000.0)

    result = await create_transaction(data, token)
    assert result.user_id == target_user.id
    assert result.amount == 5000.0
    assert result.type == "ADMIN_TOP_UP"


async def test__failed__not_admin(uow, request_create_transaction):
    user = (await create_users(uow))[0]
    target_user = (await create_users(uow))[0]
    token = create_access_token(user.as_short())
    data = TransactionFactory.build(user_id=target_user.id)

    response = await request_create_transaction(data, token)
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json()["code"] == "forbidden"


async def test__failed__unauthorized(request_create_transaction):
    data = TransactionFactory.build()
    response = await request_create_transaction(data, token="invalid")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
