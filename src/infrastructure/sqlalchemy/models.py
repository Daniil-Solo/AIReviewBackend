import sqlalchemy as sa

from src.constants.workspaces import (
    WorkspaceMemberRoleEnum,
)


metadata = sa.MetaData()

users_table = sa.Table(
    "users",
    metadata,
    sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
    sa.Column("fullname", sa.String(255), nullable=False),
    sa.Column("email", sa.String(255), nullable=False, unique=True),
    sa.Column("hashed_password", sa.String, nullable=False),
    sa.Column("is_verified", sa.Boolean, nullable=False, server_default=sa.false()),
    sa.Column("is_admin", sa.Boolean, nullable=False, server_default=sa.false()),
    sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
)

workspaces_table = sa.Table(
    "workspaces",
    metadata,
    sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
    sa.Column("name", sa.String(255), nullable=False),
    sa.Column("description", sa.Text, nullable=False, server_default=""),
    sa.Column("is_archived", sa.Boolean, nullable=False, server_default=sa.false()),
    sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
)

workspace_members_table = sa.Table(
    "workspace_members",
    metadata,
    sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
    sa.Column(
        "workspace_id",
        sa.Integer,
        sa.ForeignKey("workspaces.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
    ),
    sa.Column("user_id", sa.Integer, sa.ForeignKey("users.id", ondelete="CASCADE", onupdate="CASCADE"), nullable=False),
    sa.Column("role", sa.Enum(WorkspaceMemberRoleEnum, name="workspace_member_role"), nullable=False),
    sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    sa.UniqueConstraint("workspace_id", "user_id", name="uq_workspace_members_workspace_user"),
)

workspace_join_rules_table = sa.Table(
    "workspace_join_rules",
    metadata,
    sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
    sa.Column(
        "workspace_id",
        sa.Integer,
        sa.ForeignKey("workspaces.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
    ),
    sa.Column("slug", sa.String(255), nullable=False, unique=True),
    sa.Column("hashed_password", sa.String, nullable=True),
    sa.Column("used_count", sa.Integer, nullable=False, server_default=sa.text("0")),
    sa.Column("is_active", sa.Boolean, nullable=False, server_default=sa.true()),
    sa.Column("role", sa.Enum(WorkspaceMemberRoleEnum, name="workspace_join_rule_role"), nullable=False),
    sa.Column("expired_at", sa.DateTime(timezone=True), nullable=True),
    sa.CheckConstraint("role IN ('TEACHER', 'STUDENT')", name="chk_join_rule_role_not_owner"),
)
