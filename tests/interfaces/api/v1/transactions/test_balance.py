from fastapi import status
from httpx import AsyncClient, Response
import pytest_asyncio

from src.dto.transactions.transactions import BalanceResponseDTO
from src.infrastructure.auth import create_access_token
from tests.helpers.users import create_users


@pytest_asyncio.fixture()
def request_get_balance(client: AsyncClient):
    async def inner(token: str) -> Response:
        return await client.get(
            "/api/v1/transactions/balance",
            headers={"Authorization": f"Bearer {token}"},
        )

    return inner


@pytest_asyncio.fixture()
def get_balance(request_get_balance):
    async def inner(token: str) -> BalanceResponseDTO:
        response = await request_get_balance(token)
        assert response.status_code == status.HTTP_200_OK
        return BalanceResponseDTO.model_validate_json(response.text)

    return inner


async def test__success(uow, get_balance):
    user = (await create_users(uow))[0]
    token = create_access_token(user.as_short())

    result = await get_balance(token)
    assert result.balance == 0.0


async def test__failed__unauthorized(request_get_balance):
    response = await request_get_balance(token="invalid")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
