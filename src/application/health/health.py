import logging

from dependency_injector.wiring import Provide, inject
import sqlalchemy as sa

from src.di.container import Container
from src.infrastructure.sqlalchemy.uow import UnitOfWork


logger = logging.getLogger(__name__)


@inject
async def check(uow: UnitOfWork = Provide[Container.uow]) -> dict[str, bool]:
    data = {"postgres": True}
    try:
        async with uow:
            await uow.session.execute(sa.text("SELECT 1"))
    except Exception:
        logger.exception("Проверка Postgres")
        data["postgres"] = False
    finally:
        return data
