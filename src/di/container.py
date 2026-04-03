from dependency_injector import containers, providers

from src.infrastructure.dao.sqlalchemy.users import SQLAlchemyUsersDAO
from src.infrastructure.sqlalchemy.engine import create_engine, create_session_factory
from src.infrastructure.sqlalchemy.uow import UnitOfWork
from src.settings import settings


class Container(containers.DeclarativeContainer):
    engine = providers.Singleton(create_engine, url=settings.db.url)

    session_factory = providers.Singleton(
        create_session_factory,
        engine=engine,
    )

    users_dao = providers.Factory(lambda: SQLAlchemyUsersDAO)

    uow = providers.Factory(
        UnitOfWork,
        session_factory=session_factory,
        users_dao_factory=users_dao,
    )


def init_container() -> Container:
    container = Container()
    container.wire(packages=[
        "src.application.auth",
        "src.application.health",
        "src.application.users",
    ])
    return container
