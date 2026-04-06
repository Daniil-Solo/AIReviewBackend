from src.infrastructure.sqlalchemy.uow import UnitOfWork
from src.dto.users.user import UserCreateDTO, UserResponseDTO
from src.infrastructure.auth import hash_password
from tests.factories.users import UserFactory


async def create_users(
    uow: UnitOfWork,
    size: int = 1,
    is_admin: bool = False,
) -> list[UserResponseDTO]:
    data_list: list[UserCreateDTO] = UserFactory.build_batch(size=size)
    users = []
    async with uow.connection():
        for data in data_list:
            hashed_password = hash_password(data.password)
            user = await uow.users.create(
                email=data.email,
                fullname=data.fullname,
                hashed_password=hashed_password,
                is_admin=is_admin,
            )
            users.append(user)
    return users
