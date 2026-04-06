import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.exceptions import EntityNotFoundError
from src.dto.workspaces.workspace import WorkspaceCreateDTO, WorkspaceResponseDTO, WorkspaceUpdateDTO
from src.infrastructure.dao.workspaces.interface import WorkspacesDAO
from src.infrastructure.sqlalchemy.models import workspaces_table


class SQLAlchemyWorkspacesDAO(WorkspacesDAO):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, data: WorkspaceCreateDTO) -> WorkspaceResponseDTO:
        query = sa.insert(workspaces_table).values(**data.model_dump(by_alias=True)).returning(workspaces_table)
        result = await self.session.execute(query)
        row = result.fetchone()
        if row is None:
            raise EntityNotFoundError(message="Пространство не создано")
        return WorkspaceResponseDTO.model_validate(row)

    async def get_by_id(self, workspace_id: int) -> WorkspaceResponseDTO:
        query = sa.select(workspaces_table).where(workspaces_table.c.id == workspace_id)
        result = await self.session.execute(query)
        row = result.fetchone()
        if row is None:
            raise EntityNotFoundError(message="Пространство не найдено")
        return WorkspaceResponseDTO.model_validate(row)

    async def update(self, workspace_id: int, data: WorkspaceUpdateDTO) -> WorkspaceResponseDTO:
        query = (
            sa.update(workspaces_table)
            .where(workspaces_table.c.id == workspace_id)
            .values(**data.model_dump(by_alias=True))
            .returning(workspaces_table)
        )
        result = await self.session.execute(query)
        row = result.fetchone()
        if row is None:
            raise EntityNotFoundError(message="Пространство не найдено")
        return WorkspaceResponseDTO.model_validate(row)

    async def archive(self, workspace_id: int) -> None:
        query = sa.update(workspaces_table).where(workspaces_table.c.id == workspace_id).values(is_archived=True)
        await self.session.execute(query)
