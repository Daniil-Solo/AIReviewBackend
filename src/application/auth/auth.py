from dependency_injector.wiring import Provide, inject

from src.application.exceptions import EntityNotFoundError, InvalidCredentialsError
from src.di.container import Container
from src.dto.auth.token import TokenDTO, UserLoginDTO
from src.infrastructure.auth import create_access_token, verify_password
from src.infrastructure.sqlalchemy.uow import UnitOfWork


@inject
async def login(data: UserLoginDTO, uow: UnitOfWork = Provide[Container.uow]) -> TokenDTO:
    async with uow.connection():
        try:
            user = await uow.users.get_by_email(data.email)
        except EntityNotFoundError as ex:
            raise InvalidCredentialsError(
                message="Пользователь с таким email не существует",
                code="no_such_email_user",
            ) from ex

        if not verify_password(data.password, user.hashed_password):
            raise InvalidCredentialsError(message="Пароль неверный", code="wrong_password")

        access_token = create_access_token(user.as_short())
        return TokenDTO(access_token=access_token)
