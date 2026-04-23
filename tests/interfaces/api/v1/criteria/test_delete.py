from fastapi import status
from httpx import AsyncClient, Response
import pytest_asyncio

from src.infrastructure.auth import create_access_token
from tests.helpers.criteria import create_criteria
from tests.helpers.users import create_users


@pytest_asyncio.fixture()
def request_delete_criterion(client: AsyncClient):
    async def inner(criterion_id: int, token: str) -> Response:
        return await client.delete(
            f"/api/v1/criteria/{criterion_id}",
            headers={"Authorization": f"Bearer {token}"},
        )

    return inner


async def test__success(uow, request_delete_criterion):
    user = (await create_users(uow, is_admin=True))[0]
    token = create_access_token(user.as_short())

    criterion = (await create_criteria(uow, user.id))[0]

    response = await request_delete_criterion(criterion.id, token)
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["message"] == "Критерий удалён"


async def test__failed__not_admin(uow, request_delete_criterion):
    user = (await create_users(uow))[0]
    other_user = (await create_users(uow))[0]
    other_token = create_access_token(other_user.as_short())

    criterion = (await create_criteria(uow, user.id))[0]

    response = await request_delete_criterion(criterion.id, other_token)
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json()["code"] == "criterion_access_denied"


async def test__failed__not_found(uow, request_delete_criterion):
    user = (await create_users(uow))[0]
    token = create_access_token(user.as_short())

    response = await request_delete_criterion(9999, token)
    assert response.status_code == status.HTTP_404_NOT_FOUND


async def test__failed__unauthorized(request_delete_criterion):
    response = await request_delete_criterion(1, token="invalid")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
