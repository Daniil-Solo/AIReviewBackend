from typing import Any

import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.exceptions import EntityNotFoundError
from src.dto.workspaces.member import (
    WorkspaceMemberCreateDTO,
    WorkspaceMemberFiltersDTO,
    WorkspaceMemberResponseDTO,
    WorkspaceMemberUpdateDTO,
)
from src.infrastructure.dao.workspace_members.interface import WorkspaceMembersDAO
from src.infrastructure.sqlalchemy.models import users_table, workspace_members_table


class SQLAlchemyWorkspaceMembersDAO(WorkspaceMembersDAO):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, data: WorkspaceMemberCreateDTO) -> WorkspaceMemberResponseDTO:
        query = sa.insert(workspace_members_table).values(**data.model_dump()).returning(workspace_members_table)
        await self.session.execute(query)
        return await self._get_by_user_and_workspace(data.user_id, data.workspace_id)

    @staticmethod
    def _get_query() -> sa.Select[Any]:
        return sa.select(
            workspace_members_table.c.id,
            workspace_members_table.c.workspace_id,
            workspace_members_table.c.user_id,
            users_table.c.fullname,
            users_table.c.email,
            workspace_members_table.c.role,
        ).select_from(workspace_members_table.join(users_table, workspace_members_table.c.user_id == users_table.c.id))

    async def get_list(self, filters: WorkspaceMemberFiltersDTO) -> list[WorkspaceMemberResponseDTO]:
        query = self._get_query().where(workspace_members_table.c.workspace_id == filters.workspace_id)

        if filters.roles:
            query = query.where(workspace_members_table.c.role.in_(filters.roles))

        if filters.ids:
            query = query.where(workspace_members_table.c.user_id.in_(filters.ids))

        result = await self.session.execute(query)
        rows = result.fetchall()
        return [WorkspaceMemberResponseDTO.model_validate(row) for row in rows]

    async def get_by_user_and_workspace(self, user_id: int, workspace_id: int) -> WorkspaceMemberResponseDTO:
        return await self._get_by_user_and_workspace(user_id, workspace_id)

    async def _get_by_user_and_workspace(self, user_id: int, workspace_id: int) -> WorkspaceMemberResponseDTO:
        query = self._get_query().where(
            workspace_members_table.c.user_id == user_id,
            workspace_members_table.c.workspace_id == workspace_id,
        )
        result = await self.session.execute(query)
        row = result.fetchone()
        if row is None:
            raise EntityNotFoundError(message="Участник не найден в пространстве")
        return WorkspaceMemberResponseDTO.model_validate(row)

    async def get_by_id(self, member_id: int) -> WorkspaceMemberResponseDTO:
        query = self._get_query().where(workspace_members_table.c.id == member_id)
        result = await self.session.execute(query)
        row = result.fetchone()
        if row is None:
            raise EntityNotFoundError(message="Участник не найден")
        return WorkspaceMemberResponseDTO.model_validate(row)

    async def get_by_user(self, user_id: int) -> list[WorkspaceMemberResponseDTO]:
        query = self._get_query().where(workspace_members_table.c.user_id == user_id)
        result = await self.session.execute(query)
        rows = result.fetchall()
        return [WorkspaceMemberResponseDTO.model_validate(row) for row in rows]

    async def update(self, member_id: int, data: WorkspaceMemberUpdateDTO) -> WorkspaceMemberResponseDTO:
        query = (
            sa.update(workspace_members_table)
            .where(workspace_members_table.c.id == member_id)
            .values(**data.model_dump())
            .returning(
                workspace_members_table.c.id, workspace_members_table.c.user_id, workspace_members_table.c.workspace_id
            )
        )
        result = await self.session.execute(query)
        row = result.fetchone()
        if row is None:
            raise EntityNotFoundError(message="Участник не найден")
        return await self._get_by_user_and_workspace(row.user_id, row.workspace_id)

    async def delete(self, member_id: int) -> None:
        query = sa.delete(workspace_members_table).where(workspace_members_table.c.id == member_id)
        await self.session.execute(query)
