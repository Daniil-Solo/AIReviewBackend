import sqlalchemy as sa


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
