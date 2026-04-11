from abc import ABC, abstractmethod

from src.dto.auth.register import CodeInfoDTO


class RegistrationsFlow(ABC):
    @abstractmethod
    async def create(self, data: CodeInfoDTO) -> None:
        raise NotImplementedError

    @abstractmethod
    async def get(self, email: str) -> CodeInfoDTO | None:
        raise NotImplementedError

    @abstractmethod
    async def update_code(self, email: str, code: str) -> None:
        raise NotImplementedError

    @abstractmethod
    async def update_attempts(self, email: str, attempts: int) -> None:
        raise NotImplementedError

    @abstractmethod
    async def delete(self, email: str) -> None:
        raise NotImplementedError
