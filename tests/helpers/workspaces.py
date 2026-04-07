from src.constants.workspaces import WorkspaceMemberRoleEnum
from src.dto.workspaces.join_rule import WorkspaceJoinRuleCreateDTO
from src.dto.workspaces.member import WorkspaceMemberCreateDTO
from src.dto.workspaces.workspace import WorkspaceCreateDTO, WorkspaceResponseDTO
from src.infrastructure.auth.password import hash_password
from src.infrastructure.sqlalchemy.uow import UnitOfWork


async def create_workspace(
    uow: UnitOfWork,
    user_id: int,
    name: str | None = None,
    description: str | None = None,
) -> WorkspaceResponseDTO:
    data = WorkspaceCreateDTO(name=name or "Test Workspace", description=description or "")
    async with uow.connection() as conn, conn.transaction():
        workspace = await uow.workspaces.create(data)
        await uow.workspace_members.create(
            WorkspaceMemberCreateDTO(
                user_id=user_id,
                workspace_id=workspace.id,
                role=WorkspaceMemberRoleEnum.OWNER,
            )
        )
        return await uow.workspaces.get_by_id(workspace.id)


async def add_user_to_workspace(
    uow: UnitOfWork,
    workspace_id: int,
    user_id: int,
    role: WorkspaceMemberRoleEnum = WorkspaceMemberRoleEnum.STUDENT,
) -> None:
    async with uow.connection():
        await uow.workspace_members.create(
            WorkspaceMemberCreateDTO(
                user_id=user_id,
                workspace_id=workspace_id,
                role=role,
            )
        )


async def create_join_rule(
    uow: UnitOfWork,
    workspace_id: int,
    slug: str | None = None,
    password: str | None = None,
    role: WorkspaceMemberRoleEnum = WorkspaceMemberRoleEnum.STUDENT,
) -> None:
    hashed_password = hash_password(password) if password else None
    data = WorkspaceJoinRuleCreateDTO(
        workspace_id=workspace_id,
        slug=slug or f"test-slug-{workspace_id}",
        role=role,
        hashed_password=hashed_password,
    )
    async with uow.connection():
        await uow.workspace_join_rules.create(data)
