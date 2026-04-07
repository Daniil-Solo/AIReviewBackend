import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.exceptions import ConflictError, EntityNotFoundError
from src.dto.workspaces.join_rule import (
    WorkspaceJoinRuleCreateDTO,
    WorkspaceJoinRuleFullDTO,
    WorkspaceJoinRuleUpdateDTO,
)
from src.infrastructure.dao.workspace_join_rules.interface import WorkspaceJoinRulesDAO
from src.infrastructure.sqlalchemy.models import workspace_join_rules_table


class SQLAlchemyWorkspaceJoinRulesDAO(WorkspaceJoinRulesDAO):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(
        self,
        data: WorkspaceJoinRuleCreateDTO,
    ) -> WorkspaceJoinRuleFullDTO:
        query = sa.insert(workspace_join_rules_table).values(**data.model_dump()).returning(workspace_join_rules_table)
        try:
            result = await self.session.execute(query)
        except Exception as e:
            if "unique" in str(e).lower() or "duplicate" in str(e).lower():
                raise ConflictError(message="Слаг уже занят", code="slug_exists") from None
            raise
        row = result.fetchone()
        if row is None:
            raise EntityNotFoundError(message="Приглашение не создано")
        return WorkspaceJoinRuleFullDTO.model_validate(row)

    async def get_one(self, rule_id: int | None = None, slug: str | None = None) -> WorkspaceJoinRuleFullDTO:
        query = sa.select(workspace_join_rules_table)
        if rule_id is not None:
            query = query.where(workspace_join_rules_table.c.id == rule_id)
        elif slug is not None:
            query = query.where(workspace_join_rules_table.c.slug == slug)
        else:
            raise RuntimeError("Не передан идентификатор правила или его слаг")

        result = await self.session.execute(query)
        row = result.fetchone()
        if row is None:
            raise EntityNotFoundError(message="Приглашение не найдено")
        return WorkspaceJoinRuleFullDTO.model_validate(row)

    async def get_list(self, workspace_id: int) -> list[WorkspaceJoinRuleFullDTO]:
        query = sa.select(workspace_join_rules_table).where(workspace_join_rules_table.c.workspace_id == workspace_id)
        result = await self.session.execute(query)
        rows = result.fetchall()
        return [WorkspaceJoinRuleFullDTO.model_validate(row) for row in rows]

    async def update(self, rule_id: int, data: WorkspaceJoinRuleUpdateDTO) -> WorkspaceJoinRuleFullDTO:
        query = (
            sa.update(workspace_join_rules_table)
            .where(workspace_join_rules_table.c.id == rule_id)
            .values(**data.model_dump())
            .returning(workspace_join_rules_table)
        )
        try:
            result = await self.session.execute(query)
        except Exception as e:
            if "unique" in str(e).lower() or "duplicate" in str(e).lower():
                raise ConflictError(message="Slug уже существует", code="slug_exists") from None
            raise
        row = result.fetchone()
        if row is None:
            raise EntityNotFoundError(message="Правило приглашения не найдено")
        return WorkspaceJoinRuleFullDTO.model_validate(row)

    async def delete(self, rule_id: int) -> None:
        query = sa.delete(workspace_join_rules_table).where(workspace_join_rules_table.c.id == rule_id)
        await self.session.execute(query)

    async def increment_used_count(self, rule_id: int) -> None:
        query = (
            sa.update(workspace_join_rules_table)
            .where(workspace_join_rules_table.c.id == rule_id)
            .values(used_count=workspace_join_rules_table.c.used_count + 1)
        )
        await self.session.execute(query)

    async def exists_by_slug(self, slug: str) -> bool:
        query = sa.select(sa.exists(workspace_join_rules_table).where(workspace_join_rules_table.c.slug == slug))
        result = await self.session.execute(query)
        return bool(result.fetchone()[0])
