from abc import ABC, abstractmethod


class SolutionArtifactStorage(ABC):
    @abstractmethod
    async def save_artifact(self, solution_id: int, key: str, content: str) -> None:
        raise NotImplementedError

    @abstractmethod
    async def get_artifact(self, solution_id: int, key: str) -> str:
        raise NotImplementedError

    @abstractmethod
    async def delete_artifact(self, solution_id: int, key: str) -> None:
        raise NotImplementedError
