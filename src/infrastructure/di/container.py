from dependency_injector import containers, providers

from src.infrastructure.sqlalchemy.engine import async_session_maker
from src.infrastructure.sqlalchemy.uow import UnitOfWork


class Container(containers.DeclarativeContainer):
    wiring_config = containers.WiringConfiguration(modules=["src.application"])

    session_factory = providers.Singleton(lambda: async_session_maker)
    uow = providers.Factory(UnitOfWork, session_factory=session_factory)


def init_container():
    return Container()
