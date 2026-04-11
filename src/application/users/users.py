from dependency_injector.wiring import Provide, inject

from src.application.exceptions import ConflictError, EntityNotFoundError, ForbiddenError
from src.di.container import Container
from src.dto.users.user import ShortUserDTO, UserCreateDTO, UserResponseDTO
from src.infrastructure.auth import hash_password
from src.infrastructure.sqlalchemy.uow import UnitOfWork


@inject
async def create_user(data: UserCreateDTO, uow: UnitOfWork = Provide[Container.uow]) -> UserResponseDTO:
    async with uow.connection():
        try:
            await uow.users.get_by_email(data.email)
        except EntityNotFoundError:
            pass
        else:
            raise ConflictError(message="Пользователь с таким email уже существует", code="user_email_exists")

        hashed_password = hash_password(data.password)
        return await uow.users.create(
            email=data.email,
            fullname=data.fullname,
            hashed_password=hashed_password,
            is_admin=False,
            is_verified=False,
        )


@inject
async def create_admin(data: UserCreateDTO, uow: UnitOfWork = Provide[Container.uow]) -> UserResponseDTO:
    async with uow.connection():
        try:
            await uow.users.get_by_email(data.email)
        except EntityNotFoundError:
            pass
        else:
            raise ConflictError(message="Пользователь с таким email уже существует", code="user_email_exists")

        hashed_password = hash_password(data.password)
        return await uow.users.create(
            email=data.email,
            fullname=data.fullname,
            hashed_password=hashed_password,
            is_admin=True,
            is_verified=True,
        )


@inject
async def get_all_users(user: ShortUserDTO, uow: UnitOfWork = Provide[Container.uow]) -> list[UserResponseDTO]:
    if not user.is_admin:
        raise ForbiddenError(message="Пользователь должен быть админом", code="admin_only")

    async with uow.connection():
        return await uow.users.get_all()


@inject
async def get_user(user_id: int, uow: UnitOfWork = Provide[Container.uow]) -> UserResponseDTO:
    async with uow.connection():
        return await uow.users.get_by_id(user_id)
