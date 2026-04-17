from abc import ABC, abstractmethod

from src.dto.users.user import UserResponseDTO, UserWithPasswordDTO


class UsersDAO(ABC):
    @abstractmethod
    async def create(
        self, email: str, fullname: str, hashed_password: str, is_admin: bool = False, is_verified: bool = False
    ) -> UserResponseDTO:
        raise NotImplementedError

    @abstractmethod
    async def get_by_id(self, user_id: int) -> UserResponseDTO:
        raise NotImplementedError

    @abstractmethod
    async def get_by_email(self, email: str) -> UserWithPasswordDTO:
        raise NotImplementedError

    @abstractmethod
    async def get_all(self) -> list[UserResponseDTO]:
        raise NotImplementedError

    @abstractmethod
    async def get_by_ids(self, user_ids: list[int]) -> list[UserResponseDTO]:
        raise NotImplementedError
