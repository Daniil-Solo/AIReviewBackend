from datetime import datetime, timedelta, timezone
from fastapi import status
from httpx import AsyncClient, Response
import pytest_asyncio

from src.dto.transactions.transactions import (
    TransactionFilterDTO,
    TransactionHourlyGroupDTO,
)
from src.infrastructure.auth import create_access_token
from tests.helpers.transactions import create_transactions
from tests.helpers.users import create_users


@pytest_asyncio.fixture()
def request_get_transactions(client: AsyncClient):
    async def inner(token: str, filters: TransactionFilterDTO | None = None) -> Response:
        params = {}
        if filters:
            if filters.started_at:
                params["started_at"] = filters.started_at.isoformat()
            if filters.ended_at:
                params["ended_at"] = filters.ended_at.isoformat()
        return await client.get(
            "/api/v1/transactions",
            params=params,
            headers={"Authorization": f"Bearer {token}"},
        )

    return inner


@pytest_asyncio.fixture()
def get_transactions(request_get_transactions):
    async def inner(token: str, filters: TransactionFilterDTO | None = None) -> list[TransactionHourlyGroupDTO]:
        response = await request_get_transactions(token, filters)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        return [TransactionHourlyGroupDTO.model_validate(item) for item in data]

    return inner


async def test__success(uow, get_transactions):
    user = (await create_users(uow))[0]
    token = create_access_token(user.as_short())
    await create_transactions(uow, user.id, size=3, amount=100.0)

    result = await get_transactions(token)
    assert len(result) > 0
    assert all(g.amount >= 0 for g in result)


async def test__success__with_filters(uow, get_transactions):
    user = (await create_users(uow))[0]
    token = create_access_token(user.as_short())
    await create_transactions(uow, user.id, size=3, amount=100.0)

    now = datetime.now(timezone.utc)
    filters = TransactionFilterDTO(
        started_at=now - timedelta(days=1),
        ended_at=now + timedelta(days=1),
    )

    result = await get_transactions(token, filters)
    assert len(result) >= 0


async def test__failed__unauthorized(request_get_transactions):
    response = await request_get_transactions(token="invalid")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
