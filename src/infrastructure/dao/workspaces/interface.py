from abc import ABC, abstractmethod

from src.dto.workspaces.workspace import WorkspaceCreateDTO, WorkspaceResponseDTO, WorkspaceUpdateDTO


class WorkspacesDAO(ABC):
    @abstractmethod
    async def create(self, data: WorkspaceCreateDTO) -> WorkspaceResponseDTO:
        raise NotImplementedError

    @abstractmethod
    async def get_by_id(self, workspace_id: int) -> WorkspaceResponseDTO:
        raise NotImplementedError

    @abstractmethod
    async def update(self, workspace_id: int, data: WorkspaceUpdateDTO) -> WorkspaceResponseDTO:
        raise NotImplementedError

    @abstractmethod
    async def archive(self, workspace_id: int) -> None:
        raise NotImplementedError
