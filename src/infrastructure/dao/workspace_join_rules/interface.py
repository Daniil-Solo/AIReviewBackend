from abc import ABC, abstractmethod

from src.dto.workspaces.join_rule import (
    WorkspaceJoinRuleCreateDTO,
    WorkspaceJoinRuleFullDTO,
    WorkspaceJoinRuleUpdateDTO,
)


class WorkspaceJoinRulesDAO(ABC):
    @abstractmethod
    async def create(
        self,
        data: WorkspaceJoinRuleCreateDTO,
    ) -> WorkspaceJoinRuleFullDTO:
        raise NotImplementedError

    @abstractmethod
    async def get_one(self, rule_id: int | None = None, slug: str | None = None) -> WorkspaceJoinRuleFullDTO:
        raise NotImplementedError

    @abstractmethod
    async def get_list(self, workspace_id: int) -> list[WorkspaceJoinRuleFullDTO]:
        raise NotImplementedError

    @abstractmethod
    async def update(self, rule_id: int, data: WorkspaceJoinRuleUpdateDTO) -> WorkspaceJoinRuleFullDTO:
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
