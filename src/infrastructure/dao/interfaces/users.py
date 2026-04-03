import abc

from src.dto.users.user import UserResponseDTO


class UsersDAO(abc.ABC):
    @abc.abstractmethod
    async def create(self, email: str, fullname: str, hashed_password: str, is_admin: bool = False) -> UserResponseDTO:
        raise NotImplementedError

    @abc.abstractmethod
    async def get_by_id(self, user_id: int) -> UserResponseDTO:
        raise NotImplementedError

    @abc.abstractmethod
    async def get_by_email(self, email: str) -> UserResponseDTO:
        raise NotImplementedError

    @abc.abstractmethod
    async def get_all(self) -> list[UserResponseDTO]:
        raise NotImplementedError
