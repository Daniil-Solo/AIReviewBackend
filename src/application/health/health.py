from dependency_injector.wiring import Provide, inject
import sqlalchemy as sa

from src.di.container import Container
from src.infrastructure.logging import get_logger
from src.infrastructure.sqlalchemy.uow import UnitOfWork


logger = get_logger()


@inject
async def check(uow: UnitOfWork = Provide[Container.uow]) -> dict[str, bool]:
    data = {"postgres": True}
    try:
        async with uow.connection():
            await uow.session.execute(sa.text("SELECT 1"))
    except Exception:
        logger.exception("Healthcheck failed", component="postgres")
        data["postgres"] = False
    finally:
        return data
