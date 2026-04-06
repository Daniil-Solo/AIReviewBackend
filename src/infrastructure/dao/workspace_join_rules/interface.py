from abc import ABC, abstractmethod

from src.dto.workspaces.join_rule import (
    WorkspaceJoinRuleCreateDTO,
    WorkspaceJoinRuleResponseDTO,
    WorkspaceJoinRuleUpdateDTO,
)


class WorkspaceJoinRulesDAO(ABC):
    @abstractmethod
    async def create(
        self,
        data: WorkspaceJoinRuleCreateDTO,
    ) -> WorkspaceJoinRuleResponseDTO:
        raise NotImplementedError

    @abstractmethod
    async def get_one(self, rule_id: int | None = None, slug: str | None = None) -> WorkspaceJoinRuleResponseDTO:
        raise NotImplementedError

    @abstractmethod
    async def get_list(self, workspace_id: int) -> list[WorkspaceJoinRuleResponseDTO]:
        raise NotImplementedError

    @abstractmethod
    async def update(self, rule_id: int, data: WorkspaceJoinRuleUpdateDTO) -> WorkspaceJoinRuleResponseDTO:
        raise NotImplementedError

    @abstractmethod
    async def delete(self, rule_id: int) -> None:
        raise NotImplementedError

    @abstractmethod
    async def increment_used_count(self, rule_id: int) -> None:
        raise NotImplementedError

    @abstractmethod
    async def exists_by_slug(self, slug: str) -> bool:
        raise NotImplementedError
