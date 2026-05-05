from abc import ABC, abstractmethod
from typing import IO, Any


class SolutionStorage(ABC):
    @abstractmethod
    async def upload_solution(self, file: IO[Any], filename: str, task_id: int, user_id: int) -> str:
        raise NotImplementedError

    @abstractmethod
    async def get_content(self, key: str) -> bytes:
        raise NotImplementedError
