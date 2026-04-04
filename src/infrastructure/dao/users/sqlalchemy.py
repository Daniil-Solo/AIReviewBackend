import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.exceptions import EntityNotFoundError
from src.dto.users.user import UserResponseDTO, UserWithPasswordDTO
from src.infrastructure.dao.users.interface import UsersDAO
from src.infrastructure.sqlalchemy.models import users_table


class SQLAlchemyUsersDAO(UsersDAO):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, email: str, fullname: str, hashed_password: str, is_admin: bool = False) -> UserResponseDTO:
        query = (
            sa.insert(users_table)
            .values(
                email=email,
                fullname=fullname,
                hashed_password=hashed_password,
                is_admin=is_admin,
                is_verified=False,
            )
            .returning(users_table)
        )
        result = await self.session.execute(query)
        row = result.fetchone()
        if row is None:
            raise EntityNotFoundError(message="Пользователь не найден")
        return UserResponseDTO.model_validate(row)

    async def get_by_id(self, user_id: int) -> UserResponseDTO:
        query = sa.select(users_table).where(users_table.c.id == user_id)
        result = await self.session.execute(query)
        row = result.fetchone()
        if row is None:
            raise EntityNotFoundError(message="Пользователь не найден")
        return UserResponseDTO.model_validate(row)

    async def get_by_email(self, email: str) -> UserWithPasswordDTO:
        query = sa.select(users_table).where(users_table.c.email == email)
        result = await self.session.execute(query)
        row = result.fetchone()
        if row is None:
            raise EntityNotFoundError(message="Пользователь не найден")
        return UserWithPasswordDTO.model_validate(row)

    async def get_all(self) -> list[UserResponseDTO]:
        query = sa.select(users_table)
        result = await self.session.execute(query)
        rows = result.fetchall()
        return [UserResponseDTO.model_validate(row) for row in rows]
