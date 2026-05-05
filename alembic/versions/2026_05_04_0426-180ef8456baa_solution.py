"""solution

Revision ID: 180ef8456baa
Revises: a2d9af224e86
Create Date: 2026-05-04 04:26:09.538690

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "180ef8456baa"
down_revision: Union[str, Sequence[str], None] = "a2d9af224e86"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Обновляем старые статусы на 'ERROR' (они будут удалены из enum)
    op.execute("UPDATE solutions SET status = 'ERROR' WHERE status IN ('AI_REVIEW', 'WAITING_EXAM', 'EXAMINATION')")

    # 2. Временно меняем тип колонки на text, чтобы снять зависимость от enum
    op.execute("ALTER TABLE solutions ALTER COLUMN status TYPE text")

    # 3. Удаляем старый enum тип
    op.execute("DROP TYPE solution_status")

    # 4. Создаём новый enum тип с нужными значениями (все актуальные статусы)
    op.execute("""
        CREATE TYPE solution_status AS ENUM (
            'CREATED',
            'CANCELLED',
            'ERROR',
            'PROJECT_GENERATION',
            'VALIDATION_WAITING',
            'CRITERIA_GRADING',
            'HUMAN_REVIEW',
            'REVIEWED'
        )
    """)

    # 5. Возвращаем колонке тип enum, приводя значения через явное приведение
    op.execute("ALTER TABLE solutions ALTER COLUMN status TYPE solution_status USING status::solution_status")

    # 6. Добавляем новую колонку label (как и в оригинале)
    op.add_column("solutions", sa.Column("label", sa.String(), server_default="", nullable=False))


def downgrade() -> None:
    # 1. Удаляем колонку label
    op.drop_column("solutions", "label")

    # 2. Статусы, появившиеся в upgrade, заменяем на 'ERROR' (старый enum их не содержит)
    op.execute("UPDATE solutions SET status = 'ERROR' WHERE status IN ('PROJECT_GENERATION', 'VALIDATION_WAITING', 'CRITERIA_GRADING')")

    # 3. Временно меняем тип колонки на text
    op.execute("ALTER TABLE solutions ALTER COLUMN status TYPE text")

    # 4. Удаляем текущий enum (с новыми значениями)
    op.execute("DROP TYPE solution_status")

    # 5. Воссоздаём исходный enum с удаляемыми значениями 'AI_REVIEW', 'WAITING_EXAM', 'EXAMINATION'
    op.execute("""
        CREATE TYPE solution_status AS ENUM (
            'CREATED',
            'CANCELLED',
            'ERROR',
            'HUMAN_REVIEW',
            'REVIEWED',
            'AI_REVIEW',
            'WAITING_EXAM',
            'EXAMINATION'
        )
    """)

    # 6. Возвращаем колонке тип enum
    op.execute("ALTER TABLE solutions ALTER COLUMN status TYPE solution_status USING status::solution_status")