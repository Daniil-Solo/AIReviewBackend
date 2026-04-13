from abc import ABC, abstractmethod

from src.dto.workspaces.member import (
    WorkspaceMemberCreateDTO,
    WorkspaceMemberFiltersDTO,
    WorkspaceMemberResponseDTO,
    WorkspaceMemberUpdateDTO,
)


class WorkspaceMembersDAO(ABC):
    @abstractmethod
    async def create(self, data: WorkspaceMemberCreateDTO) -> WorkspaceMemberResponseDTO:
        raise NotImplementedError

    @abstractmethod
    async def get_list(self, filters: WorkspaceMemberFiltersDTO) -> list[WorkspaceMemberResponseDTO]:
        raise NotImplementedError

    @abstractmethod
    async def get_by_user_and_workspace(self, user_id: int, workspace_id: int) -> WorkspaceMemberResponseDTO:
        raise NotImplementedError

    @abstractmethod
    async def get_by_id(self, member_id: int) -> WorkspaceMemberResponseDTO:
        raise NotImplementedError

    @abstractmethod
    async def update(self, member_id: int, data: WorkspaceMemberUpdateDTO) -> WorkspaceMemberResponseDTO:
        raise NotImplementedError

    @abstractmethod
    async def get_by_user(self, user_id: int) -> list[WorkspaceMemberResponseDTO]:
        raise NotImplementedError

    @abstractmethod
    async def delete(self, member_id: int) -> None:
        raise NotImplementedError
