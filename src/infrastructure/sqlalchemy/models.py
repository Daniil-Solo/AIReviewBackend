import sqlalchemy as sa

from src.constants.ai_review import (
    CriterionCheckStatusEnum,
    CriterionStageEnum,
    SolutionFormatEnum,
    SolutionStatusEnum,
)
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

criteria_table = sa.Table(
    "criteria",
    metadata,
    sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
    sa.Column("description", sa.Text, nullable=False),
    sa.Column("tags", sa.ARRAY(sa.String), nullable=False, server_default="{}"),
    sa.Column("stage", sa.Enum(CriterionStageEnum, name="criterion_stage"), nullable=True),
    sa.Column("is_public", sa.Boolean, nullable=False, server_default=sa.true()),
    sa.Column(
        "created_by", sa.Integer, sa.ForeignKey("users.id", ondelete="CASCADE", onupdate="CASCADE"), nullable=False
    ),
    sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
)

tasks_table = sa.Table(
    "tasks",
    metadata,
    sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
    sa.Column(
        "workspace_id",
        sa.Integer,
        sa.ForeignKey("workspaces.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
    ),
    sa.Column("name", sa.String(255), nullable=False),
    sa.Column("description", sa.Text, nullable=False, server_default=""),
    sa.Column("is_active", sa.Boolean, nullable=False, server_default=sa.true()),
    sa.Column(
        "created_by", sa.Integer, sa.ForeignKey("users.id", ondelete="CASCADE", onupdate="CASCADE"), nullable=False
    ),
    sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    sa.Column("use_exam", sa.Boolean, nullable=False, server_default=sa.false()),
)

task_criteria_table = sa.Table(
    "task_criteria",
    metadata,
    sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
    sa.Column(
        "task_id",
        sa.Integer,
        sa.ForeignKey("tasks.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
    ),
    sa.Column(
        "criterion_id",
        sa.Integer,
        sa.ForeignKey("criteria.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
    ),
    sa.Column("weight", sa.Float, nullable=False),
    sa.UniqueConstraint("task_id", "criterion_id", name="uq_task_criteria_task_criterion"),
)

solutions_table = sa.Table(
    "solutions",
    metadata,
    sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
    sa.Column(
        "task_id",
        sa.Integer,
        sa.ForeignKey("tasks.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
    ),
    sa.Column("format", sa.Enum(SolutionFormatEnum, name="solution_format"), nullable=False),
    sa.Column("link", sa.String, nullable=False),
    sa.Column("status", sa.Enum(SolutionStatusEnum, name="solution_status"), nullable=False),
    sa.Column("steps", sa.JSON, nullable=False, server_default=sa.text("'{}'")),
    sa.Column("human_grade", sa.Integer, nullable=True),
    sa.Column("human_feedback", sa.String, nullable=True),
    sa.Column("ai_feedback", sa.Text, nullable=True),
    sa.Column(
        "created_by", sa.Integer, sa.ForeignKey("users.id", ondelete="CASCADE", onupdate="CASCADE"), nullable=False
    ),
    sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
)

solution_criteria_checks_table = sa.Table(
    "solution_criteria_checks",
    metadata,
    sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
    sa.Column(
        "task_criterion_id",
        sa.Integer,
        sa.ForeignKey("task_criteria.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
    ),
    sa.Column(
        "solution_id",
        sa.Integer,
        sa.ForeignKey("solutions.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
    ),
    sa.Column("comment", sa.Text, nullable=False, server_default=""),
    sa.Column("stage", sa.Enum(CriterionStageEnum, name="solution_criterion_stage"), nullable=False),
    sa.Column(
        "status",
        sa.Enum(CriterionCheckStatusEnum, name="solution_criterion_check_status"),
        nullable=False,
    ),
    sa.Column("is_passed", sa.Boolean, nullable=True),
    sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
)

pipeline_tasks_table = sa.Table(
    "pipeline_tasks",
    metadata,
    sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
    sa.Column(
        "solution_id",
        sa.Integer,
        sa.ForeignKey("solutions.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
    ),
    sa.Column("step", sa.String(100), nullable=False),
    sa.Column("status", sa.String(20), nullable=False, server_default="pending"),
    sa.Column("error_text", sa.Text, nullable=True),
    sa.Column("duration", sa.Float, nullable=True),
    sa.Column("last_checked_at", sa.DateTime(timezone=True), nullable=True),
    sa.Column("ran_at", sa.DateTime(timezone=True), nullable=True),
    sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    sa.UniqueConstraint("solution_id", "step", name="uq_pipeline_tasks_solution_step"),
    sa.Index("ix_pipeline_tasks_last_checked_at", "last_checked_at"),
)

transactions_table = sa.Table(
    "transactions",
    metadata,
    sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
    sa.Column("user_id", sa.Integer, sa.ForeignKey("users.id", ondelete="CASCADE", onupdate="CASCADE"), nullable=False),
    sa.Column("amount", sa.Float, nullable=False),
    sa.Column("type",  sa.String(100), nullable=False),
    sa.Column("metadata", sa.JSON, nullable=True),
    sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
)

ALL_TABLES = [
    users_table,
    workspaces_table,
    workspace_members_table,
    workspace_join_rules_table,
    criteria_table,
    tasks_table,
    task_criteria_table,
    solutions_table,
    solution_criteria_checks_table,
    pipeline_tasks_table,
    transactions_table,
]
