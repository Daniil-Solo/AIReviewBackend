===== FILE: dev.docker-compose.yaml =====
version: "3.9"
services:
  postgres:
    image: postgres:14.8-alpine3.18
    container_name: dev_postgres
    environment:
      PGDATA: "/var/lib/postgresql/data/pgdata"
    env_file: ".env"
    volumes:
      - aithc-data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U $POSTGRES_USER -d $POSTGRES_DB"]
      interval: 10s
      timeout: 5s
      retries: 5
      start_period: 10s
    restart: unless-stopped
    deploy:
      resources:
        limits:
          cpus: '1'
          memory: 2G

  redis:
    image: redis:latest
    container_name: dev_redis
    env_file: ".env"
    ports:
      - "6379:6379"
    volumes:
      - cache-data:/data
    deploy:
      resources:
        limits:
          cpus: '0.50'
          memory: 512M
        reservations:
          cpus: '0.25'
          memory: 256M
    command: >
      sh -c '
        mkdir -p /usr/local/etc/redis &&
        echo "bind 0.0.0.0" > /usr/local/etc/redis/redis.conf &&
        echo "requirepass $REDIS_PASSWORD" >> /usr/local/etc/redis/redis.conf &&
        echo "appendonly yes" >> /usr/local/etc/redis/redis.conf &&
        echo "appendfsync everysec" >> /usr/local/etc/redis/redis.conf &&
        echo "user default on nopass ~* +@all" > /usr/local/etc/redis/users.acl &&
        echo "user $REDIS_USER on >$REDIS_USER_PASSWORD ~* +@all" >> /usr/local/etc/redis/users.acl &&
        redis-server /usr/local/etc/redis/redis.conf --aclfile /usr/local/etc/redis/users.acl
      '
    healthcheck:
      test: [ "CMD", "redis-cli", "-a", "$REDIS_PASSWORD", "ping" ]
      interval: 30s
      timeout: 10s
      retries: 5
    restart: unless-stopped
    tty: true
    stdin_open: true

volumes:
  aithc-data:
  cache-data:
===== END FILE =====

===== FILE: entrypoint.sh =====
#!/bin/bash

cd /app
.venv/bin/python -m alembic upgrade head
cd ..
/app/.venv/bin/python -m uvicorn src.app:app --host 0.0.0.0 --port 5000
===== END FILE =====

===== FILE: pyproject.toml =====
[tool.poetry]
name = "aith-courses"
version = "0.1.0"
description = ""
authors = ["Daniil-Solo <daniil.solo1723@gmail.com>"]
readme = "README.md"

[tool.poetry.dependencies]
python = "^3.11"
fastapi = "^0.111.0"
pydantic-settings = "^2.3.4"
uvicorn = "^0.30.1"
sqlalchemy = "^2.0.31"
asyncpg = "^0.29.0"
alembic = "^1.13.2"
redis = "^5.0.7"


[tool.poetry.group.dev.dependencies]
ruff = "^0.5.0"

[tool.poetry.group.test.dependencies]
pytest = "^8.2.2"
httpx = "^0.27.0"
pytest-asyncio = "^0.23.7"
pytest-dotenv = "^0.5.2"

[build-system]
requires = ["poetry-core"]
build-backend = "poetry.core.masonry.api"

[pytest]
python_files = "test_*.py"

[tool.pytest.ini_options]
asyncio_mode = "auto"
env_files =	[".test.env"]
testpaths = [
    "unit_tests",
    "integration_tests",
]

[tool.ruff]
fix=true
unsafe-fixes=false
line-length = 120
lint.select = ["ALL"]
lint.ignore = [
    "D211", "D213", "D100", "D104", "D102", "D107", "ANN003", "B008", "PLR0913", "TCH003",
    "RUF001", "RUF003", "DTZ001", "DTZ003", "DTZ005", "ARG001"
]
extend-include = ["*.ipynb"]
lint.allowed-confusables = ["с"]
===== END FILE =====

===== FILE: readme.md =====
# Core Backend

[![Linters Status](https://github.com/AITH-Courses/CoreBackend/actions/workflows/linters.yaml/badge.svg?branch=master)](https://github.com/AITH-Courses/CoreBackend/actions/workflows/linters.yaml)

## Разработка
### Окружение для разработки
```bash
docker-compose -f dev.docker-compose.yaml up -d
```

### Запуск приложения
```bash
poetry run uvicorn src.app:app --port 5000 --reload
```

### Миграции
```bash
poetry run alembic revision --autogenerate -m "Comment"
poetry run alembic upgrade head
```

### Линтеры
```bash
poetry run ruff check src
```

## Тестирование
### Окружение для тестирования
```bash
docker-compose -f test.docker-compose.yaml up -d
```

### Тесты
```bash
poetry run pytest -v unit_tests 
poetry run pytest -v integration_tests

```
===== END FILE =====

===== FILE: test.docker-compose.yaml =====
version: "3.9"
services:
  postgres:
    image: postgres:14.8-alpine3.18
    container_name: test_postgres
    environment:
      PGDATA: "/var/lib/postgresql/data/pgdata"
    env_file: ".test.env"
    volumes:
      - aithc-test-data:/var/lib/postgresql/data
    ports:
      - "5431:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U $POSTGRES_USER -d aithc-test"]
      interval: 10s
      timeout: 5s
      retries: 5
      start_period: 10s
    restart: unless-stopped
    deploy:
      resources:
        limits:
          cpus: '1'
          memory: 2G

  redis:
    image: redis:latest
    container_name: test_redis
    env_file: ".test.env"
    ports:
      - "6378:6379"
    volumes:
      - cache-test-data:/data
    deploy:
      resources:
        limits:
          cpus: '0.50'
          memory: 512M
        reservations:
          cpus: '0.25'
          memory: 256M
    command: >
      sh -c '
        mkdir -p /usr/local/etc/redis &&
        echo "bind 0.0.0.0" > /usr/local/etc/redis/redis.conf &&
        echo "requirepass $REDIS_PASSWORD" >> /usr/local/etc/redis/redis.conf &&
        echo "appendonly yes" >> /usr/local/etc/redis/redis.conf &&
        echo "appendfsync everysec" >> /usr/local/etc/redis/redis.conf &&
        echo "user default on nopass ~* +@all" > /usr/local/etc/redis/users.acl &&
        echo "user $REDIS_USER on >$REDIS_USER_PASSWORD ~* +@all" >> /usr/local/etc/redis/users.acl &&
        redis-server /usr/local/etc/redis/redis.conf --aclfile /usr/local/etc/redis/users.acl
      '
    healthcheck:
      test: [ "CMD", "redis-cli", "-a", "$REDIS_PASSWORD", "ping" ]
      interval: 30s
      timeout: 10s
      retries: 5
    restart: unless-stopped
    tty: true
    stdin_open: true

volumes:
  aithc-test-data:
  cache-test-data:
===== END FILE =====

===== FILE: alembic/env.py =====
from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

from src.config import app_config
from src.infrastructure.sqlalchemy.session import Base
from src.infrastructure.sqlalchemy.users.models import User
from src.infrastructure.sqlalchemy.courses.models import Course, RunForCourse, RoleForCourse, PeriodForCourse
from src.infrastructure.sqlalchemy.feedback.models import Feedback, VoteForFeedback
from src.infrastructure.sqlalchemy.course_run.models import CourseRun
from src.infrastructure.sqlalchemy.timetable.models import TimetableRule
from src.infrastructure.sqlalchemy.talent_profile.models import TalentProfile
from src.infrastructure.sqlalchemy.favorite_courses.models import FavoriteCourse
from src.infrastructure.sqlalchemy.group_google_calendar.models import GroupGoogleCalendar
from src.infrastructure.sqlalchemy.playlists.models import Playlist

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config
config.set_main_option("sqlalchemy.url", app_config.db_url + "?async_fallback=True")


# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
target_metadata = Base.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()

===== END FILE =====

===== FILE: alembic/versions/2504c51722b5_course.py =====
"""course

Revision ID: 2504c51722b5
Revises: e967288e19c5
Create Date: 2024-07-09 19:27:23.025544

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2504c51722b5'
down_revision: Union[str, None] = 'e967288e19c5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('courses',
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('image_url', sa.String(), nullable=True),
    sa.Column('limits', sa.Integer(), nullable=True),
    sa.Column('is_draft', sa.Boolean(), nullable=False),
    sa.Column('is_archive', sa.Boolean(), nullable=False),
    sa.Column('prerequisites', sa.Text(), nullable=True),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('topics', sa.Text(), nullable=True),
    sa.Column('assessment', sa.Text(), nullable=True),
    sa.Column('resources', sa.Text(), nullable=True),
    sa.Column('extra', sa.Text(), nullable=True),
    sa.Column('author', sa.String(), nullable=True),
    sa.Column('implementer', sa.String(), nullable=True),
    sa.Column('format', sa.String(), nullable=True),
    sa.Column('terms', sa.String(), nullable=True),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text("TIMEZONE('utc', now())"), nullable=False),
    sa.Column('updated_at', sa.DateTime(), server_default=sa.text("TIMEZONE('utc', now())"), nullable=False),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_courses')),
    sa.UniqueConstraint('name', name=op.f('uq_courses_name'))
    )
    op.create_table('course_periods',
    sa.Column('course_id', sa.Uuid(), nullable=False),
    sa.Column('period_name', sa.String(), nullable=False),
    sa.ForeignKeyConstraint(['course_id'], ['courses.id'], name=op.f('fk_course_periods_course_id_courses')),
    sa.PrimaryKeyConstraint('course_id', 'period_name', name=op.f('pk_course_periods'))
    )
    op.create_table('course_roles',
    sa.Column('course_id', sa.Uuid(), nullable=False),
    sa.Column('role_name', sa.String(), nullable=False),
    sa.ForeignKeyConstraint(['course_id'], ['courses.id'], name=op.f('fk_course_roles_course_id_courses')),
    sa.PrimaryKeyConstraint('course_id', 'role_name', name=op.f('pk_course_roles'))
    )
    op.create_table('course_runs',
    sa.Column('course_id', sa.Uuid(), nullable=False),
    sa.Column('run_name', sa.String(), nullable=False),
    sa.ForeignKeyConstraint(['course_id'], ['courses.id'], name=op.f('fk_course_runs_course_id_courses')),
    sa.PrimaryKeyConstraint('course_id', 'run_name', name=op.f('pk_course_runs'))
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('course_runs')
    op.drop_table('course_roles')
    op.drop_table('course_periods')
    op.drop_table('courses')
    # ### end Alembic commands ###

===== END FILE =====

===== FILE: alembic/versions/3b078e034715_google_calendar_link.py =====
"""google_calendar_link

Revision ID: 3b078e034715
Revises: 3cdc89b052bc
Create Date: 2024-09-08 18:51:13.857715

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3b078e034715'
down_revision: Union[str, None] = '3cdc89b052bc'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('group_google_calendars',
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('course_run_id', sa.Uuid(), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('link', sa.String(), nullable=False),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text("TIMEZONE('utc', now())"), nullable=False),
    sa.Column('updated_at', sa.DateTime(), server_default=sa.text("TIMEZONE('utc', now())"), nullable=False),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_group_google_calendars'))
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('group_google_calendars')
    # ### end Alembic commands ###

===== END FILE =====

===== FILE: alembic/versions/3cdc89b052bc_favorite_courses.py =====
"""favorite courses

Revision ID: 3cdc89b052bc
Revises: b3632baf5773
Create Date: 2024-08-30 02:53:21.939483

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3cdc89b052bc'
down_revision: Union[str, None] = 'b3632baf5773'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('favorite_courses',
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('user_id', sa.Uuid(), nullable=False),
    sa.Column('course_id', sa.Uuid(), nullable=False),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text("TIMEZONE('utc', now())"), nullable=False),
    sa.Column('updated_at', sa.DateTime(), server_default=sa.text("TIMEZONE('utc', now())"), nullable=False),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_favorite_courses')),
    sa.UniqueConstraint('user_id', 'course_id', name='uix_course_id_user_id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('favorite_courses')
    # ### end Alembic commands ###

===== END FILE =====

===== FILE: alembic/versions/68cc9f3338b1_course_run_timetable.py =====
"""course_run_timetable

Revision ID: 68cc9f3338b1
Revises: b85ab4c1beaf
Create Date: 2024-08-20 02:29:13.091042

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '68cc9f3338b1'
down_revision: Union[str, None] = 'b85ab4c1beaf'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('course_runs_',
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('course_id', sa.Uuid(), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('is_archive', sa.Boolean(), nullable=False),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text("TIMEZONE('utc', now())"), nullable=False),
    sa.Column('updated_at', sa.DateTime(), server_default=sa.text("TIMEZONE('utc', now())"), nullable=False),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_course_runs_')),
    sa.UniqueConstraint('course_id', 'name', name='uix_course_id_name')
    )
    op.create_table('timetable_rules',
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('rule_type', sa.String(), nullable=False),
    sa.Column('start_time', sa.Time(), nullable=False),
    sa.Column('end_time', sa.Time(), nullable=False),
    sa.Column('start_period_date', sa.Date(), nullable=False),
    sa.Column('end_period_date', sa.Date(), nullable=False),
    sa.Column('weekdays', sa.String(), nullable=True),
    sa.Column('course_run_id', sa.Uuid(), nullable=False),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text("TIMEZONE('utc', now())"), nullable=False),
    sa.Column('updated_at', sa.DateTime(), server_default=sa.text("TIMEZONE('utc', now())"), nullable=False),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_timetable_rules'))
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('timetable_rules')
    op.drop_table('course_runs_')
    # ### end Alembic commands ###

===== END FILE =====

===== FILE: alembic/versions/b1ecf9cd86c0_feedback_and_votes.py =====
"""feedback and votes

Revision ID: b1ecf9cd86c0
Revises: 2504c51722b5
Create Date: 2024-07-28 16:56:09.154737

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b1ecf9cd86c0'
down_revision: Union[str, None] = '2504c51722b5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('feedbacks',
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('course_id', sa.Uuid(), nullable=False),
    sa.Column('author_id', sa.Uuid(), nullable=False),
    sa.Column('content', sa.Text(), nullable=False),
    sa.Column('date', sa.Date(), nullable=False),
    sa.Column('is_archive', sa.Boolean(), nullable=False),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text("TIMEZONE('utc', now())"), nullable=False),
    sa.Column('updated_at', sa.DateTime(), server_default=sa.text("TIMEZONE('utc', now())"), nullable=False),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_feedbacks'))
    )
    op.create_table('feedback_votes',
    sa.Column('feedback_id', sa.Uuid(), nullable=False),
    sa.Column('user_id', sa.Uuid(), nullable=False),
    sa.Column('vote_type', sa.String(), nullable=False),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text("TIMEZONE('utc', now())"), nullable=False),
    sa.ForeignKeyConstraint(['feedback_id'], ['feedbacks.id'], name=op.f('fk_feedback_votes_feedback_id_feedbacks')),
    sa.PrimaryKeyConstraint('feedback_id', 'user_id', name=op.f('pk_feedback_votes'))
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('feedback_votes')
    op.drop_table('feedbacks')
    # ### end Alembic commands ###

===== END FILE =====

===== FILE: alembic/versions/b3632baf5773_profile.py =====
"""profile

Revision ID: b3632baf5773
Revises: 68cc9f3338b1
Create Date: 2024-08-29 19:50:57.469239

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b3632baf5773'
down_revision: Union[str, None] = '68cc9f3338b1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('talent_profiles',
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('image_url', sa.String(), nullable=True),
    sa.Column('location', sa.String(), nullable=False),
    sa.Column('position', sa.String(), nullable=False),
    sa.Column('company', sa.String(), nullable=False),
    sa.Column('link_ru_resume', sa.String(), nullable=False),
    sa.Column('link_eng_resume', sa.String(), nullable=False),
    sa.Column('link_tg_personal', sa.String(), nullable=False),
    sa.Column('link_linkedin', sa.String(), nullable=False),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text("TIMEZONE('utc', now())"), nullable=False),
    sa.Column('updated_at', sa.DateTime(), server_default=sa.text("TIMEZONE('utc', now())"), nullable=False),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_talent_profiles'))
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('talent_profiles')
    # ### end Alembic commands ###

===== END FILE =====

===== FILE: alembic/versions/b85ab4c1beaf_rating_for_feedback.py =====
"""rating for feedback

Revision ID: b85ab4c1beaf
Revises: b1ecf9cd86c0
Create Date: 2024-07-30 20:05:29.798664

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b85ab4c1beaf'
down_revision: Union[str, None] = 'b1ecf9cd86c0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('feedbacks', sa.Column('rating', sa.Integer(), server_default='5', nullable=False))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('feedbacks', 'rating')
    # ### end Alembic commands ###

===== END FILE =====

===== FILE: alembic/versions/d21fb58adff2_init_db.py =====
"""Init DB

Revision ID: d21fb58adff2
Revises: 
Create Date: 2024-07-03 11:23:03.101514

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd21fb58adff2'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    pass
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    pass
    # ### end Alembic commands ###

===== END FILE =====

===== FILE: alembic/versions/e29544b891d8_playlists.py =====
"""playlists

Revision ID: e29544b891d8
Revises: 3b078e034715
Create Date: 2024-09-19 15:05:33.287189

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e29544b891d8'
down_revision: Union[str, None] = '3b078e034715'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('playlists',
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('course_run_id', sa.Uuid(), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('type', sa.String(), nullable=False),
    sa.Column('link', sa.String(), nullable=False),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text("TIMEZONE('utc', now())"), nullable=False),
    sa.Column('updated_at', sa.DateTime(), server_default=sa.text("TIMEZONE('utc', now())"), nullable=False),
    sa.PrimaryKeyConstraint('id', 'course_run_id', name=op.f('pk_playlists'))
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('playlists')
    # ### end Alembic commands ###

===== END FILE =====

===== FILE: alembic/versions/e967288e19c5_user.py =====
"""User

Revision ID: e967288e19c5
Revises: d21fb58adff2
Create Date: 2024-07-05 13:18:38.581808

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e967288e19c5'
down_revision: Union[str, None] = 'd21fb58adff2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('users',
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('firstname', sa.String(), nullable=False),
    sa.Column('lastname', sa.String(), nullable=False),
    sa.Column('role', sa.String(), nullable=False),
    sa.Column('email', sa.String(), nullable=False),
    sa.Column('hashed_password', sa.String(), nullable=False),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text("TIMEZONE('utc', now())"), nullable=False),
    sa.Column('updated_at', sa.DateTime(), server_default=sa.text("TIMEZONE('utc', now())"), nullable=False),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_users')),
    sa.UniqueConstraint('email', name=op.f('uq_users_email'))
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('users')
    # ### end Alembic commands ###

===== END FILE =====

===== FILE: integration_tests/__init__.py =====

===== END FILE =====

===== FILE: integration_tests/conftest.py =====
import asyncio
from typing import AsyncGenerator
import pytest
from fastapi import FastAPI
from httpx import AsyncClient, ASGITransport
from redis import asyncio as aioredis
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncEngine, AsyncSession

from src.app import create_application
from src.config import app_config
from src.infrastructure.sqlalchemy.session import async_engine, Base


@pytest.fixture(scope="session")
def test_app() -> FastAPI:
    app = create_application()
    return app


@pytest.fixture(scope="session")
async def async_client(test_app) -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(
            transport=ASGITransport(app=test_app),
            base_url="http://localhost"
    ) as ac:
        yield ac


@pytest.fixture(scope='function')
async def async_db_engine():
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield async_engine
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture(scope='function')
async def test_async_session(async_db_engine: AsyncEngine):
    async_session_factory = async_sessionmaker(
        bind=async_db_engine,
        autocommit=False,
        expire_on_commit=False,
        autoflush=False,
        class_=AsyncSession,
    )
    async with async_session_factory() as session:
        yield session


@pytest.fixture(scope='function')
async def test_cache_session():
    async with aioredis.from_url(app_config.cache_url) as session:
        await session.flushall()
        yield session
        await session.flushall()


@pytest.fixture(scope='session')
def event_loop():
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    yield loop
    loop.close()

===== END FILE =====

===== FILE: integration_tests/auth/__init__.py =====

===== END FILE =====

===== FILE: integration_tests/auth/test_repositories.py =====
import uuid

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.auth.entities import UserEntity
from src.domain.auth.exceptions import UserNotFoundError
from src.domain.auth.value_objects import PartOfName, UserRole, Email
from src.domain.base_value_objects import UUID
from src.infrastructure.sqlalchemy.users.repository import SQLAlchemyUserRepository


async def create_user(async_session: AsyncSession) -> tuple[UUID, SQLAlchemyUserRepository]:
    repo = SQLAlchemyUserRepository(async_session)
    user_id = UUID(str(uuid.uuid4()))
    await repo.create(UserEntity(
        id=user_id,
        firstname=PartOfName("Nick"),
        lastname=PartOfName("Cargo"),
        role=UserRole("admin"),
        email=Email("nick@cargo.com"),
        hashed_password="32rserfs4t4ts4t4"
    ))
    await async_session.commit()
    return user_id, repo


async def test_create_user(test_async_session: AsyncSession):
    user_id, repo = await create_user(test_async_session)
    user = await repo.get_by_id(user_id)
    assert user.role == UserRole("admin")
    assert user.firstname == PartOfName("Nick")
    assert user.lastname == PartOfName("Cargo")
    assert user.email == Email("nick@cargo.com")


async def test_update_user(test_async_session: AsyncSession):
    user_id, repo = await create_user(test_async_session)
    user = await repo.get_by_id(user_id)
    user.firstname = PartOfName("Andrew")
    user.email = Email("andrew@mail.com")
    await repo.update(user)
    await test_async_session.commit()
    assert user.firstname == PartOfName("Andrew")
    assert user.email == Email("andrew@mail.com")


async def test_delete_user(test_async_session: AsyncSession):
    user_id, repo = await create_user(test_async_session)
    await repo.delete(user_id)
    await test_async_session.commit()
    with pytest.raises(UserNotFoundError):
        await repo.get_by_id(user_id)


async def test_get_another_email(test_async_session: AsyncSession):
    user_id, repo = await create_user(test_async_session)
    with pytest.raises(UserNotFoundError):
        await repo.get_by_email(Email("another@mail.ru"))

===== END FILE =====

===== FILE: integration_tests/auth/test_session_service.py =====
import uuid

import pytest

from src.domain.auth.entities import UserEntity
from src.domain.auth.exceptions import UserBySessionNotFoundError
from src.domain.auth.value_objects import PartOfName, UserRole, Email
from src.domain.base_value_objects import UUID
from src.infrastructure.redis.auth.session_service import RedisSessionService


@pytest.fixture(scope='function')
def redis_session_service(test_cache_session):
    return RedisSessionService(test_cache_session)


async def test_set_get_user(redis_session_service):
    auth_token = "auth-token"
    user = UserEntity(
        id=UUID(str(uuid.uuid4())),
        firstname=PartOfName("Nick"),
        lastname=PartOfName("Cargo"),
        role=UserRole("admin"),
        email=Email("nick@cargo.com"),
        hashed_password="32rserfs4t4ts4t4"
    )
    await redis_session_service.set(auth_token, user)
    user_in_cache = await redis_session_service.get(auth_token)
    assert user_in_cache.id == user.id
    assert user_in_cache.email == user.email
    assert user_in_cache.firstname == user.firstname
    assert user_in_cache.lastname == user.lastname
    assert user_in_cache.role == user.role
    assert user_in_cache.email == user.email
    assert user_in_cache.hashed_password == user.hashed_password


async def test_no_user(redis_session_service):
    auth_token = "auth-token"
    with pytest.raises(UserBySessionNotFoundError):
        await redis_session_service.get(auth_token)


async def test_delete_user(redis_session_service):
    auth_token = "auth-token"
    user = UserEntity(
        id=UUID(str(uuid.uuid4())),
        firstname=PartOfName("Nick"),
        lastname=PartOfName("Cargo"),
        role=UserRole("admin"),
        email=Email("nick@cargo.com"),
        hashed_password="32rserfs4t4ts4t4"
    )
    await redis_session_service.set(auth_token, user)
    await redis_session_service.delete(auth_token)
    with pytest.raises(UserBySessionNotFoundError):
        await redis_session_service.get(auth_token)


async def test_update_user(redis_session_service):
    auth_token = "auth-token"
    user = UserEntity(
        id=UUID(str(uuid.uuid4())),
        firstname=PartOfName("Nick"),
        lastname=PartOfName("Cargo"),
        role=UserRole("admin"),
        email=Email("nick@cargo.com"),
        hashed_password="32rserfs4t4ts4t4"
    )
    await redis_session_service.set(auth_token, user)
    updated_user = UserEntity(
        id=UUID(str(uuid.uuid4())),
        firstname=PartOfName("Carl"),
        lastname=PartOfName("Cargo"),
        role=UserRole("admin"),
        email=Email("nick@cargo.com"),
        hashed_password="32rserfs4t4ts4t4"
    )
    await redis_session_service.update(auth_token, updated_user)
    user_in_cache = await redis_session_service.get(auth_token)
    assert user_in_cache.id == updated_user.id
    assert user_in_cache.email == updated_user.email
    assert user_in_cache.firstname == updated_user.firstname
    assert user_in_cache.lastname == updated_user.lastname
    assert user_in_cache.role == updated_user.role
    assert user_in_cache.email == updated_user.email
    assert user_in_cache.hashed_password == updated_user.hashed_password

===== END FILE =====

===== FILE: integration_tests/course_run/__init__.py =====

===== END FILE =====

===== FILE: integration_tests/course_run/test_repostitory.py =====
import uuid

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.base_value_objects import UUID
from src.domain.course_run.entities import CourseRunEntity
from src.domain.course_run.exceptions import CourseRunNotFoundError
from src.domain.courses.value_objects import CourseRun
from src.infrastructure.sqlalchemy.course_run.repository import SQLAlchemyCourseRunRepository


async def create_course_run(async_session: AsyncSession, course_id: UUID, name: str) -> tuple[UUID, SQLAlchemyCourseRunRepository]:
    repo = SQLAlchemyCourseRunRepository(async_session)
    course_run_id = UUID(str(uuid.uuid4()))
    await repo.create(CourseRunEntity(
        id=course_run_id,
        course_id=course_id,
        name=CourseRun(name)
    ))
    await async_session.commit()
    return course_run_id, repo


async def test_create_course_run(test_async_session: AsyncSession):
    course_id = UUID(str(uuid.uuid4()))
    course_run_id, repo = await create_course_run(test_async_session, course_id, "Весна 2024")
    course_run = await repo.get_by_id(course_run_id)
    assert course_run.id == course_run_id
    assert course_run.course_id == course_id
    assert course_run.name == CourseRun("Весна 2024")


async def test_get_all_course_runs(test_async_session: AsyncSession):
    course_id = UUID(str(uuid.uuid4()))
    course_run_1_id, _ = await create_course_run(test_async_session, course_id, "Весна 2024")
    course_run_2_id, repo = await create_course_run(test_async_session, course_id, "Весна 2025")
    courses = await repo.get_all_by_course_id(course_id)
    assert len(courses) == 2
    assert courses[0].id == course_run_2_id
    assert courses[1].id == course_run_1_id


async def test_delete_course_run(test_async_session: AsyncSession):
    course_id = UUID(str(uuid.uuid4()))
    course_run_1_id, repo = await create_course_run(test_async_session, course_id, "Весна 2024")
    await repo.delete(course_run_1_id)
    await test_async_session.commit()
    with pytest.raises(CourseRunNotFoundError):
        await repo.get_by_id(course_run_1_id)

===== END FILE =====

===== FILE: integration_tests/courses/__init__.py =====

===== END FILE =====

===== FILE: integration_tests/courses/test_course_cache_service.py =====
import uuid

import pytest

from src.domain.base_value_objects import UUID
from src.domain.courses.entities import CourseEntity
from src.domain.courses.value_objects import CourseName, CourseRun
from src.infrastructure.redis.courses.course_cache_service import RedisCourseCacheService


@pytest.fixture(scope='function')
def redis_course_cache_service(test_cache_session):
    return RedisCourseCacheService(test_cache_session, "test")


async def test_operations_with_one_course(redis_course_cache_service):
    course_id = UUID(str(uuid.uuid4()))
    course = CourseEntity(
        id=course_id,
        name=CourseName("Алгоритмизация"),
        last_runs=[CourseRun("Весна 2023"), CourseRun("Осень 2024")]
    )
    await redis_course_cache_service.set_one(course)

    getting_course = await redis_course_cache_service.get_one(course_id)
    assert getting_course.id == course.id
    assert getting_course.name == course.name
    assert getting_course.limits == course.limits
    assert len(getting_course.roles) == 0
    assert len(getting_course.last_runs) == 2
    assert getting_course.last_runs[0] == course.last_runs[0]
    assert getting_course.last_runs[1] == course.last_runs[1]

    await redis_course_cache_service.delete_one(course_id)

    deleted_course = await redis_course_cache_service.get_one(course_id)
    assert deleted_course is None


async def test_operations_with_all_courses(redis_course_cache_service):
    course_1 = CourseEntity(
        id=UUID(str(uuid.uuid4())),
        name=CourseName("Алгоритмизация")
    )
    course_2 = CourseEntity(
        id=UUID(str(uuid.uuid4())),
        name=CourseName("Java")
    )
    await redis_course_cache_service.set_many([course_1, course_2])

    getting_courses = await redis_course_cache_service.get_many()
    assert len(getting_courses) == 2
    assert getting_courses[0].name == CourseName("Алгоритмизация")
    assert getting_courses[1].name == CourseName("Java")

    await redis_course_cache_service.delete_many()

    deleted_courses = await redis_course_cache_service.get_many()
    assert deleted_courses is None

===== END FILE =====

===== FILE: integration_tests/courses/test_repostitory.py =====
import uuid

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.base_value_objects import UUID
from src.domain.courses.constants import PERIODS, ROLES
from src.domain.courses.entities import CourseEntity
from src.domain.courses.exceptions import CourseNotFoundError
from src.domain.courses.value_objects import CourseName, Period, Role, CourseRun
from src.infrastructure.sqlalchemy.courses.repository import SQLAlchemyCourseRepository


async def create_course(async_session: AsyncSession) -> tuple[UUID, SQLAlchemyCourseRepository]:
    repo = SQLAlchemyCourseRepository(async_session)
    course_id = UUID(str(uuid.uuid4()))
    await repo.create(CourseEntity(
        id=course_id,
        name=CourseName("Алгоритмизация")
    ))
    await async_session.commit()
    return course_id, repo


async def test_create_course(test_async_session: AsyncSession):
    course_id, repo = await create_course(test_async_session)
    course = await repo.get_by_id(course_id)
    assert course.id == course_id
    assert course.name == CourseName("Алгоритмизация")
    assert course.image_url is None
    assert len(course.roles) == 0
    assert len(course.periods) == 0
    assert len(course.last_runs) == 0


async def test_get_many_courses(test_async_session: AsyncSession):
    course_id, repo = await create_course(test_async_session)
    courses = await repo.get_all()
    assert len(courses) == 1
    assert courses[0].id == course_id
    assert courses[0].name == CourseName("Алгоритмизация")
    assert courses[0].image_url is None
    assert len(courses[0].roles) == 0
    assert len(courses[0].periods) == 0
    assert len(courses[0].last_runs) == 0


async def test_update_course(test_async_session: AsyncSession):
    course_id, repo = await create_course(test_async_session)
    update_course = CourseEntity(
        course_id,
        name=CourseName("Методы алгоритмизации"),
        image_url="image/path-to-file.png",
        roles=[Role(ROLES[0])],
        periods=[Period(PERIODS[0])],
        last_runs=[CourseRun("Весна 2023")],
    )
    await repo.update(update_course)
    await test_async_session.commit()
    course = await repo.get_by_id(course_id)
    assert course.id == course_id
    assert course.name == CourseName("Методы алгоритмизации")
    assert course.image_url == "image/path-to-file.png"
    assert course.implementer is None
    assert course.format is None
    assert course.terms is None
    assert course.author is None
    assert len(course.roles) == len(update_course.roles)
    assert course.roles[0] == update_course.roles[0]
    assert len(course.periods) == len(update_course.periods)
    assert course.periods[0] == update_course.periods[0]
    assert len(course.last_runs) == len(update_course.last_runs)
    assert course.last_runs[0] == update_course.last_runs[0]


async def test_delete_course(test_async_session: AsyncSession):
    course_id, repo = await create_course(test_async_session)
    await repo.delete(course_id)
    await test_async_session.commit()
    with pytest.raises(CourseNotFoundError):
        await repo.get_by_id(course_id)


async def test_update_course_after_delete(test_async_session: AsyncSession):
    course_id, repo = await create_course(test_async_session)
    await repo.delete(course_id)
    await test_async_session.commit()
    with pytest.raises(CourseNotFoundError):
        update_course = CourseEntity(
            course_id,
            name=CourseName("Методы алгоритмизации"),
        )
        await repo.update(update_course)
        await test_async_session.commit()

===== END FILE =====

===== FILE: integration_tests/feedback/__init__.py =====

===== END FILE =====

===== FILE: integration_tests/feedback/test_feedback_cache_service.py =====
import datetime
import uuid

import pytest

from src.domain.base_value_objects import UUID
from src.domain.feedback.entities import FeedbackEntity
from src.domain.feedback.value_objects import FeedbackText, Vote, Rating
from src.infrastructure.redis.feedback.feedback_cache_service import RedisFeedbackCacheService


@pytest.fixture(scope='function')
def redis_feedback_cache_service(test_cache_session):
    return RedisFeedbackCacheService(test_cache_session)


async def test_operations_with_one_course(redis_feedback_cache_service):
    feedback_id = UUID(str(uuid.uuid4()))
    course_id = UUID(str(uuid.uuid4()))
    author_id = UUID(str(uuid.uuid4()))
    feedbacks = [FeedbackEntity(
        id=feedback_id,
        course_id=course_id,
        author_id=author_id,
        text=FeedbackText("Cool"),
        rating=Rating(5),
        votes={Vote(UUID(str(uuid.uuid4())), "like")},
        date=datetime.date.today()
    )]
    await redis_feedback_cache_service.set_many(course_id, feedbacks)

    getting_feedbacks = await redis_feedback_cache_service.get_many_by_course_id(course_id)
    assert len(getting_feedbacks) == 1
    assert len(getting_feedbacks[0].votes) == 1
    assert getting_feedbacks[0].text.value == "Cool"
    assert getting_feedbacks[0].rating.value == 5

    await redis_feedback_cache_service.delete_many(course_id)

    deleted_course = await redis_feedback_cache_service.get_many_by_course_id(course_id)
    assert deleted_course is None

===== END FILE =====

===== FILE: integration_tests/feedback/test_repostitory.py =====
import datetime
import uuid

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.base_value_objects import UUID
from src.domain.feedback.entities import FeedbackEntity
from src.domain.feedback.exceptions import FeedbackNotFoundError
from src.domain.feedback.value_objects import FeedbackText, Rating
from src.infrastructure.sqlalchemy.feedback.repository import SQLAlchemyFeedbackRepository


async def create_feedback(async_session: AsyncSession) -> tuple[UUID, UUID, UUID, SQLAlchemyFeedbackRepository]:
    repo = SQLAlchemyFeedbackRepository(async_session)
    feedback_id = UUID(str(uuid.uuid4()))
    course_id = UUID(str(uuid.uuid4()))
    author_id = UUID(str(uuid.uuid4()))
    await repo.create(FeedbackEntity(
        id=feedback_id,
        course_id=course_id,
        author_id=author_id,
        text=FeedbackText("Cool"),
        rating=Rating(5)
    ))
    await async_session.commit()
    return feedback_id, course_id, author_id, repo


async def test_create_feedback(test_async_session: AsyncSession):
    feedback_id, course_id, author_id, repo = await create_feedback(test_async_session)
    feedback = await repo.get_one_by_id(feedback_id)
    assert feedback.id == feedback_id
    assert feedback.course_id == course_id
    assert feedback.author_id == author_id
    assert len(feedback.votes) == 0
    assert feedback.date == datetime.date.today()


async def test_get_many_feedbacks(test_async_session: AsyncSession):
    feedback_1_id, course_id, author_id, repo = await create_feedback(test_async_session)
    feedback_2_id = UUID(str(uuid.uuid4()))
    another_author_id = UUID(str(uuid.uuid4()))
    await repo.create(FeedbackEntity(
        id=feedback_2_id,
        course_id=course_id,
        author_id=another_author_id,
        text=FeedbackText("Cool 2"),
        rating=Rating(5),
        date=datetime.date.today() + datetime.timedelta(days=1)
    ))
    await test_async_session.commit()
    feedbacks = await repo.get_all_by_course_id(course_id)
    assert len(feedbacks) == 2
    assert feedbacks[0].id == feedback_2_id
    assert feedbacks[1].id == feedback_1_id


async def test_add_votes(test_async_session: AsyncSession):
    feedback_id, _, _, repo = await create_feedback(test_async_session)
    feedback = await repo.get_one_by_id(feedback_id)
    feedback.vote(UUID(str(uuid.uuid4())), "like")
    feedback.vote(UUID(str(uuid.uuid4())), "dislike")
    await repo.update_votes(feedback)
    await test_async_session.commit()

    updated_feedback = await repo.get_one_by_id(feedback_id)
    assert updated_feedback.id == feedback_id
    assert len(updated_feedback.votes) == 2
    assert updated_feedback.reputation == 0


async def test_delete_feedback(test_async_session: AsyncSession):
    feedback_id, _, _, repo = await create_feedback(test_async_session)
    await repo.delete(feedback_id)
    await test_async_session.commit()
    with pytest.raises(FeedbackNotFoundError):
        await repo.get_one_by_id(feedback_id)

===== END FILE =====

===== FILE: integration_tests/timetable/__init__.py =====

===== END FILE =====

===== FILE: integration_tests/timetable/test_repostitory.py =====
import datetime
import uuid

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.base_value_objects import UUID
from src.domain.course_run.exceptions import CourseRunNotFoundError
from src.domain.courses.value_objects import CourseRun
from src.domain.timetable.entities import TimetableEntity, DayRuleEntity, WeekRuleEntity
from src.domain.timetable.exceptions import RuleNotFoundError
from src.domain.timetable.value_objects import Weekday
from src.infrastructure.sqlalchemy.timetable.repository import SQLAlchemyTimetableRepository


async def test_create_day_rule(test_async_session: AsyncSession):
    repo = SQLAlchemyTimetableRepository(test_async_session)
    year, month, day = 2024, 12, 1
    h1, m1, h2, m2 = 17, 0, 18, 30
    course_run_id = UUID(str(uuid.uuid4()))
    rule = DayRuleEntity(
        id=UUID(str(uuid.uuid4())),
        timetable_id=course_run_id,
        start_time=datetime.time(h1, m1),
        end_time=datetime.time(h2, m2),
        date=datetime.date(year, month, day),
    )
    await repo.create_rule(rule)
    await test_async_session.commit()
    timetable = await repo.get_by_id(course_run_id)
    assert len(timetable.rules) == 1
    assert timetable.rules[0] == rule


async def test_update_day_rule(test_async_session: AsyncSession):
    repo = SQLAlchemyTimetableRepository(test_async_session)
    course_run_id = UUID(str(uuid.uuid4()))
    year, month, day = 2024, 12, 1
    h1, m1, h2, m2 = 17, 0, 18, 30
    rule_id = UUID(str(uuid.uuid4()))
    rule = DayRuleEntity(
        id=rule_id,
        timetable_id=course_run_id,
        start_time=datetime.time(h1, m1),
        end_time=datetime.time(h2, m2),
        date=datetime.date(year, month, day),
    )
    await repo.create_rule(rule)
    await test_async_session.commit()
    new_day, new_h1, new_m2 = 2, 16, 40
    await repo.update_rule(
        DayRuleEntity(
            id=rule_id,
            timetable_id=course_run_id,
            start_time=datetime.time(new_h1, m1),
            end_time=datetime.time(h2, new_m2),
            date=datetime.date(year, month, new_day),
        )
    )
    await test_async_session.commit()
    timetable = await repo.get_by_id(course_run_id)
    assert len(timetable.rules) == 1
    assert timetable.rules[0].date == datetime.date(year, month, new_day)
    assert timetable.rules[0].start_time == datetime.time(new_h1, m1)
    assert timetable.rules[0].end_time == datetime.time(h2, new_m2)


async def test_create_week_rule(test_async_session: AsyncSession):
    repo = SQLAlchemyTimetableRepository(test_async_session)
    course_run_id = UUID(str(uuid.uuid4()))
    year, month, day = 2024, 12, 1
    h1, m1, h2, m2 = 17, 0, 18, 30
    rule = WeekRuleEntity(
        id=UUID(str(uuid.uuid4())),
        timetable_id=course_run_id,
        start_time=datetime.time(h1, m1, 0),
        end_time=datetime.time(h2, m2, 0),
        start_period_date=datetime.date(year, month, day),
        end_period_date=datetime.date(year, month, day),
        weekdays=[Weekday("пн")]
    )
    await repo.create_rule(rule)
    await test_async_session.commit()
    timetable = await repo.get_by_id(course_run_id)
    assert len(timetable.rules) == 1
    assert timetable.rules[0] == rule


async def test_delete_rule(test_async_session: AsyncSession):
    repo = SQLAlchemyTimetableRepository(test_async_session)
    course_run_id = UUID(str(uuid.uuid4()))
    year, month, day = 2024, 12, 1
    h1, m1, h2, m2 = 17, 0, 18, 30
    rule_id = UUID(str(uuid.uuid4()))
    rule = DayRuleEntity(
        id=rule_id,
        timetable_id=course_run_id,
        start_time=datetime.time(h1, m1),
        end_time=datetime.time(h2, m2),
        date=datetime.date(year, month, day),
    )
    await repo.create_rule(rule)
    await test_async_session.commit()
    await repo.delete_rule(rule_id)
    await test_async_session.commit()
    with pytest.raises(RuleNotFoundError):
        await repo.delete_rule(rule_id)

===== END FILE =====

===== FILE: src/__init__.py =====

===== END FILE =====

===== FILE: src/app.py =====
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from src.api.admin.course_run.router import router as admin_course_run_router
from src.api.admin.courses.router import router as admin_course_router
from src.api.admin.group_google_calendar.integration_router import router as integration_group_google_calendar_router
from src.api.admin.group_google_calendar.router import router as group_google_calendar_router
from src.api.admin.playlists.router import router as admin_playlists_router
from src.api.admin.timetable.router import router as admin_timetable_router
from src.api.auth.router import router as auth_router
from src.api.base_schemas import ErrorResponse
from src.api.courses.router import router as course_router
from src.api.favorite_courses.router import router as favorite_courses_router
from src.api.feedback.router import router as feedback_router
from src.api.health_check import router as health_check_router
from src.api.playlists.router import router as playlists_router
from src.api.talent_profile.router import router as talent_profile_router
from src.api.timetable.router import router as course_timetable_router
from src.config import app_config
from src.domain.base_exceptions import IncorrectUUIDError
from src.exceptions import ApplicationError
from src.infrastructure.fastapi.docs import add_custom_docs_endpoints


def add_exception_handler(application: FastAPI) -> None:
    """Add exception handlers into FastAPI-application.

    :param application:
    :return:
    """

    @application.exception_handler(ApplicationError)
    async def handle_application_error(_: Request, exc: ApplicationError) -> JSONResponse:
        """Handle application error.

        :param _:
        :param exc:
        :return: JSONResponse
        """
        return JSONResponse(
            status_code=exc.status,
            content=ErrorResponse(message=exc.message).model_dump(),
        )

    @application.exception_handler(IncorrectUUIDError)
    async def handler_incorrect_uuid_error(_: Request, exc: IncorrectUUIDError) -> JSONResponse:
        """Handle incorrect uuid error.

        :param _:
        :param exc:
        :return: JSONResponse
        """
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=ErrorResponse(message=exc.message).model_dump(),
        )


def add_routers(application: FastAPI) -> None:
    """Add routers into FastAPI-application.

    :param application:
    :return: nothing
    """
    routers = [
        health_check_router, auth_router, course_router, course_timetable_router, feedback_router,
        admin_course_router, admin_course_run_router, admin_timetable_router, talent_profile_router,
        favorite_courses_router, group_google_calendar_router, integration_group_google_calendar_router,
        admin_playlists_router, playlists_router,
    ]
    for router in routers:
        application.include_router(router=router, prefix="/api/v1")


def add_cors(application: FastAPI) -> None:
    """Add routers into FastAPI-application.

    :param application:
    :return: nothing
    """
    application.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


def create_application() -> FastAPI:
    """Create FastAPI-application.

    :return: FastAPI
    """
    application = FastAPI(
        title="AITH Courses",
        version="0.0.1",
        docs_url=None,
        redoc_url=None,
    )
    if app_config.is_debug:
        add_custom_docs_endpoints(application)
    add_routers(application)
    add_exception_handler(application)
    if app_config.is_debug:
        add_cors(application)
    return application


app = create_application()

===== END FILE =====

===== FILE: src/config.py =====
from enum import Enum

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class ApplicationMode(Enum):

    """Variants of application mode."""

    DEV = "dev"
    PRODUCTION = "production"
    TEST = "test"


class Config(BaseSettings):

    """Class for loading the necessary env variables."""

    POSTGRES_DB: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_PORT: str
    POSTGRES_HOST: str
    REDIS_USER: str
    REDIS_USER_PASSWORD: str
    REDIS_PORT: str
    REDIS_HOST: str

    MODE: ApplicationMode = Field(default=ApplicationMode.PRODUCTION)

    @property
    def is_debug(self) -> bool:
        """Gets true if application in dev mode else false."""
        return self.MODE == ApplicationMode.DEV

    @staticmethod
    def __generate_asyncpg_db_url(
            user: str, password: str, host: str, port: str, database_name: str,
    ) -> str:
        """Get asynpg database url.

        :param user:
        :param password:
        :param host:
        :param port:
        :param database_name:
        :return: dns
        """
        return f"postgresql+asyncpg://{user}:{password}@{host}:{port}/{database_name}"

    @property
    def db_url(self) -> str:
        """Get DSN for database."""
        return self.__generate_asyncpg_db_url(
            self.POSTGRES_USER, self.POSTGRES_PASSWORD, self.POSTGRES_HOST,
            self.POSTGRES_PORT, self.POSTGRES_DB,
        )

    @staticmethod
    def __get_redis_cache_url(user: str, password: str, host: str, port: str) -> str:
        """Get redis cache url.

        :param user:
        :param password:
        :param host:
        :param port:
        :return: dns
        """
        return f"redis://{user}:{password}@{host}:{port}/0"

    @property
    def cache_url(self) -> str:
        """Get DSN to cache."""
        return self.__get_redis_cache_url(
            self.REDIS_USER, self.REDIS_USER_PASSWORD, self.REDIS_HOST, self.REDIS_PORT,
        )

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


app_config = Config()

===== END FILE =====

===== FILE: src/exceptions.py =====
class ApplicationError(Exception):

    """Base class with http-response fields."""

    def __init__(self, message: str, status: int) -> None:
        """Initialize object.

        :param message: human text about error
        :param status: http status code
        """
        self.message = message
        self.status = status

===== END FILE =====

===== FILE: src/api/__init__.py =====

===== END FILE =====

===== FILE: src/api/base_pagination.py =====
from __future__ import annotations

import math
from typing import Generic, TypeVar

T = TypeVar("T")


class PaginationError(Exception):

    """Base pagination error."""

    @property
    def message(self) -> str:
        return "Some pagination error"


class PageNumberMoreMaxPageError(PaginationError):

    """Error if page > max page."""

    @property
    def message(self) -> str:
        return "This page is more than count of pages"


class PageNumberLessOneError(PaginationError):

    """Error if page < 1."""

    @property
    def message(self) -> str:
        return "This page is less than 1"


class Paginator(Generic[T]):

    """Class for base pagination."""

    def __init__(self, data: list[T], page_size: int) -> None:
        self.n_pages = math.ceil(len(data) / page_size)
        self.page_size = page_size
        self.data = data

    def get_data_by_page(self, page: int) -> list[T]:
        if page > self.n_pages:
            raise PageNumberMoreMaxPageError
        if page < 0:
            raise PageNumberLessOneError
        start_index = (page - 1) * self.page_size
        last_index = page * self.page_size
        return self.data[start_index:last_index]

    @property
    def pages(self) -> list[int]:
        return list(range(1, self.n_pages + 1))

===== END FILE =====

===== FILE: src/api/base_schemas.py =====
from pydantic import BaseModel, Field


class ErrorResponse(BaseModel):

    """Schema of error operation."""

    message: str = Field(examples=["Произошла ошибка"])


class SuccessResponse(BaseModel):

    """Schema of success operation."""

    message: str = Field(examples=["Операция успешно выполнена"])

===== END FILE =====

===== FILE: src/api/health_check.py =====
from fastapi import APIRouter, status
from pydantic import BaseModel, Field

router = APIRouter(tags=["monitoring"])


class Health(BaseModel):

    """Health response."""

    status: str = Field(examples=["ok"])


@router.get(
    "/health_check",
    status_code=status.HTTP_200_OK,
    description="Check health of service",
    summary="Health check",
    responses={
        status.HTTP_200_OK: {
            "model": Health,
            "description": "Service is alive",
        },
    },
)
def health_check() -> Health:
    """Check health of service.

    :return: Health
    """
    return Health(status="ok")

===== END FILE =====

===== FILE: src/api/admin/__init__.py =====

===== END FILE =====

===== FILE: src/api/admin/course_run/__init__.py =====

===== END FILE =====

===== FILE: src/api/admin/course_run/dependencies.py =====
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.infrastructure.sqlalchemy.course_run.unit_of_work import SQLAlchemyCourseRunUnitOfWork
from src.infrastructure.sqlalchemy.session import get_async_session
from src.services.course_run.command_service import CourseRunCommandService


def get_admin_course_run_command_service(
    db_session: AsyncSession = Depends(get_async_session),
) -> CourseRunCommandService:
    """Get feedback service on sessions.

    :param db_session:
    :return:
    """
    unit_of_work = SQLAlchemyCourseRunUnitOfWork(db_session)
    return CourseRunCommandService(unit_of_work)

===== END FILE =====

===== FILE: src/api/admin/course_run/router.py =====
from fastapi import APIRouter, Body, Depends, status
from fastapi.responses import JSONResponse

from src.api.admin.course_run.dependencies import get_admin_course_run_command_service
from src.api.admin.course_run.schemas import CourseRunDTO, CreateCourseRunRequest, CreateCourseRunResponse
from src.api.admin.courses.dependencies import get_admin
from src.api.base_schemas import ErrorResponse, SuccessResponse
from src.domain.auth.entities import UserEntity
from src.domain.course_run.exceptions import CourseRunAlreadyExistsError, CourseRunNotFoundError
from src.domain.courses.exceptions import IncorrectCourseRunNameError
from src.services.course_run.command_service import CourseRunCommandService

router = APIRouter(prefix="/admin/courses/{course_id}/runs", tags=["admin"])


@router.get(
    "",
    status_code=status.HTTP_200_OK,
    description="Get all runs for course",
    summary="Get course runs",
    responses={
        status.HTTP_200_OK: {
            "model": list[CourseRunDTO],
            "description": "All course runs",
        },
    },
    response_model=list[CourseRunDTO],
)
async def get_all_course_runs(
    course_id: str,
    _: UserEntity = Depends(get_admin),
    command_service: CourseRunCommandService = Depends(get_admin_course_run_command_service),
) -> JSONResponse:
    """Get course runs.

    :return:
    """
    course_runs = await command_service.get_all_course_runs_by_id(course_id)
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=([CourseRunDTO.from_domain(run).model_dump() for run in course_runs]),
    )


@router.get(
    "/{course_run_id}",
    status_code=status.HTTP_200_OK,
    description="Get course run",
    summary="Get course run",
    responses={
        status.HTTP_200_OK: {
            "model": list[CourseRunDTO],
            "description": "One course run",
        },
        status.HTTP_404_NOT_FOUND: {
            "model": ErrorResponse,
            "description": "Error with page",
        },
    },
    response_model=list[CourseRunDTO],
)
async def get_one_course_run(
    course_id: str,
    course_run_id: str,
    _: UserEntity = Depends(get_admin),
    command_service: CourseRunCommandService = Depends(get_admin_course_run_command_service),
) -> JSONResponse:
    """Get course run.

    :return:
    """
    try:
        course_run = await command_service.get_course_run_by_id(course_run_id)
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=CourseRunDTO.from_domain(course_run).model_dump(),
        )
    except CourseRunNotFoundError as ex:
        return JSONResponse(
            content=ErrorResponse(message=ex.message).model_dump(),
            status_code=status.HTTP_404_NOT_FOUND,
        )


@router.post(
    "",
    status_code=status.HTTP_200_OK,
    description="Create course run",
    summary="Create course run",
    responses={
        status.HTTP_201_CREATED: {
            "model": CreateCourseRunResponse,
            "description": "Course run has been created",
        },
        status.HTTP_422_UNPROCESSABLE_ENTITY: {
            "model": ErrorResponse,
            "description": "Validation error",
        },
        status.HTTP_400_BAD_REQUEST: {
            "model": ErrorResponse,
            "description": "Error",
        },
    },
    response_model=CreateCourseRunResponse,
)
async def create_course_run(
    course_id: str,
    data: CreateCourseRunRequest = Body(),
    _: UserEntity = Depends(get_admin),
    command_service: CourseRunCommandService = Depends(get_admin_course_run_command_service),
) -> JSONResponse:
    """Create course run.

    :return:
    """
    try:
        course_run_id = await command_service.create_course_run(course_id, data.season, data.year)
        return JSONResponse(
            status_code=status.HTTP_201_CREATED,
            content=CreateCourseRunResponse(course_run_id=course_run_id).model_dump(),
        )
    except IncorrectCourseRunNameError as ex:
        return JSONResponse(
            content=ErrorResponse(message=ex.message).model_dump(),
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        )
    except CourseRunAlreadyExistsError as ex:
        return JSONResponse(
            content=ErrorResponse(message=ex.message).model_dump(),
            status_code=status.HTTP_400_BAD_REQUEST,
        )


@router.delete(
    "/{course_run_id}",
    status_code=status.HTTP_200_OK,
    description="Delete course run",
    summary="Delete course run",
    responses={
        status.HTTP_200_OK: {
            "model": CreateCourseRunResponse,
            "description": "Course run has been deleted",
        },
        status.HTTP_404_NOT_FOUND: {
            "model": ErrorResponse,
            "description": "Error",
        },
    },
    response_model=SuccessResponse,
)
async def delete_course_run(
    course_id: str,
    course_run_id: str,
    _: UserEntity = Depends(get_admin),
    command_service: CourseRunCommandService = Depends(get_admin_course_run_command_service),
) -> JSONResponse:
    """Delete course run.

    :return:
    """
    try:
        await command_service.delete_course_run(course_run_id)
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=SuccessResponse(message="Запуск курса успешно удален").model_dump(),
        )
    except CourseRunNotFoundError as ex:
        return JSONResponse(
            content=ErrorResponse(message=ex.message).model_dump(),
            status_code=status.HTTP_404_NOT_FOUND,
        )

===== END FILE =====

===== FILE: src/api/admin/course_run/schemas.py =====
from pydantic import BaseModel

from src.domain.course_run.entities import CourseRunEntity


class CreateCourseRunRequest(BaseModel):

    """Schema of create course run request."""

    season: str
    year: int


class CreateCourseRunResponse(BaseModel):

    """Schema of create course run response."""

    course_run_id: str


class CourseRunDTO(BaseModel):

    """Schema of course run."""

    id: str
    course_id: str
    name: str

    @staticmethod
    def from_domain(course_run: CourseRunEntity) -> "CourseRunDTO":
        return CourseRunDTO(
            id=course_run.id.value,
            course_id=course_run.course_id.value,
            name=course_run.name.value,
        )

===== END FILE =====

===== FILE: src/api/admin/courses/__init__.py =====

===== END FILE =====

===== FILE: src/api/admin/courses/dependencies.py =====
from fastapi import Depends, status
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.auth.dependencies import get_user
from src.domain.auth.entities import UserEntity
from src.exceptions import ApplicationError
from src.infrastructure.redis.courses.course_cache_service import RedisCourseCacheService
from src.infrastructure.redis.session import get_redis_session
from src.infrastructure.sqlalchemy.courses.repository import SQLAlchemyCourseRepository
from src.infrastructure.sqlalchemy.session import get_async_session
from src.services.courses.query_service_for_admin import AdminCourseQueryService


async def get_admin(
    user: UserEntity = Depends(get_user),
) -> UserEntity:
    """Get admin.

    :param user:
    :return:
    """
    if user.role.value != "admin":
        raise ApplicationError(
            message="Недостаточно прав для совершения операции",
            status=status.HTTP_403_FORBIDDEN,
        )
    return user


def get_admin_courses_query_service(
    db_session: AsyncSession = Depends(get_async_session),
    cache_session: Redis = Depends(get_redis_session),
) -> AdminCourseQueryService:
    """Get courses service on sessions for admin.

    :param db_session:
    :param cache_session:
    :return:
    """
    course_repo = SQLAlchemyCourseRepository(db_session)
    course_cache_service = RedisCourseCacheService(cache_session, "admin")
    return AdminCourseQueryService(course_repo, course_cache_service)

===== END FILE =====

===== FILE: src/api/admin/courses/router.py =====
from __future__ import annotations

from typing import TYPE_CHECKING

from fastapi import APIRouter, Body, Depends, Path, status
from fastapi.responses import JSONResponse

from src.api.admin.courses.dependencies import get_admin, get_admin_courses_query_service
from src.api.admin.courses.schemas import CreateCourseRequest, CreateCourseResponse, UpdateCourseRequest
from src.api.base_schemas import ErrorResponse, SuccessResponse
from src.api.courses.dependencies import get_courses_command_service, get_talent_courses_query_service
from src.api.courses.schemas import CourseFullDTO, CourseShortDTO
from src.domain.courses.exceptions import (
    CourseAlreadyExistsError,
    CourseNotFoundError,
    CoursePublishError,
    EmptyPropertyError,
    IncorrectCourseRunNameError,
    ValueDoesntExistError,
)

if TYPE_CHECKING:
    from src.domain.auth.entities import UserEntity
    from src.services.courses.command_service import CourseCommandService
    from src.services.courses.query_service_for_admin import AdminCourseQueryService
    from src.services.courses.query_service_for_talent import TalentCourseQueryService

router = APIRouter(prefix="/admin/courses", tags=["admin"])


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    description="Create new course",
    summary="Create course",
    responses={
        status.HTTP_201_CREATED: {
            "model": CreateCourseResponse,
            "description": "Course created",
        },
        status.HTTP_400_BAD_REQUEST: {
            "model": ErrorResponse,
            "description": "Error",
        },
        status.HTTP_422_UNPROCESSABLE_ENTITY: {
            "model": ErrorResponse,
            "description": "Error",
        },
    },
    response_model=CreateCourseResponse,
)
async def create_course(
    data: CreateCourseRequest = Body(),
    _: UserEntity = Depends(get_admin),
    command_service: CourseCommandService = Depends(get_courses_command_service),
    admin_query_service: AdminCourseQueryService = Depends(get_admin_courses_query_service),
    talent_query_service: TalentCourseQueryService = Depends(get_talent_courses_query_service),
) -> JSONResponse:
    """Create course.

    :param admin_query_service:
    :param talent_query_service:
    :param _:
    :param query_service:
    :param data:
    :param command_service:
    :return:
    """
    try:
        course_id = await command_service.create_course(data.name)
        await admin_query_service.course_cache_service.delete_many()
        await talent_query_service.course_cache_service.delete_many()
        return JSONResponse(
            content=CreateCourseResponse(course_id=course_id).model_dump(),
            status_code=status.HTTP_201_CREATED,
        )
    except CourseAlreadyExistsError as ex:
        return JSONResponse(
            content=ErrorResponse(message=ex.message).model_dump(),
            status_code=status.HTTP_400_BAD_REQUEST,
        )
    except EmptyPropertyError as ex:
        return JSONResponse(
            content=ErrorResponse(message=ex.message).model_dump(),
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        )


@router.put(
    "/{course_id}",
    status_code=status.HTTP_200_OK,
    description="Update course",
    summary="Update course",
    responses={
        status.HTTP_200_OK: {
            "model": SuccessResponse,
            "description": "Course updated",
        },
        status.HTTP_404_NOT_FOUND: {
            "model": ErrorResponse,
            "description": "No course",
        },
        status.HTTP_400_BAD_REQUEST: {
            "model": ErrorResponse,
            "description": "Error",
        },
        status.HTTP_422_UNPROCESSABLE_ENTITY: {
            "model": ErrorResponse,
            "description": "Validation error",
        },
    },
    response_model=SuccessResponse,
)
async def update_course(
    course_id: str = Path(),
    data: UpdateCourseRequest = Body(),
    _: UserEntity = Depends(get_admin),
    command_service: CourseCommandService = Depends(get_courses_command_service),
    admin_query_service: AdminCourseQueryService = Depends(get_admin_courses_query_service),
    talent_query_service: TalentCourseQueryService = Depends(get_talent_courses_query_service),
) -> JSONResponse:
    """Create course.

    :param talent_query_service:
    :param admin_query_service:
    :param _:
    :param course_id:
    :param data:
    :param command_service:
    :return:
    """
    try:
        await command_service.update_course(
            course_id=course_id, name_=data.name,
            image_url=data.image_url, limits_=data.limits,
            prerequisites_=data.prerequisites,
            description_=data.description, topics_=data.topics,
            assessment_=data.assessment, resources_=[res.model_dump() for res in data.resources],
            extra_=data.extra, author_=data.author,
            implementer_=data.implementer, format_=data.format,
            terms_=data.terms, roles=data.roles,
            periods=data.periods, runs=data.last_runs,
        )
        await admin_query_service.invalidate_course(course_id)
        await talent_query_service.invalidate_course(course_id)
        await admin_query_service.course_cache_service.delete_many()
        await talent_query_service.course_cache_service.delete_many()
        return JSONResponse(
            content=SuccessResponse(message="Course has updated").model_dump(),
            status_code=status.HTTP_200_OK,
        )
    except CourseAlreadyExistsError as ex:
        return JSONResponse(
            content=ErrorResponse(message=ex.message).model_dump(),
            status_code=status.HTTP_400_BAD_REQUEST,
        )
    except (EmptyPropertyError, IncorrectCourseRunNameError, ValueDoesntExistError) as ex:
        return JSONResponse(
            content=ErrorResponse(message=ex.message).model_dump(),
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        )
    except CourseNotFoundError as ex:
        return JSONResponse(
            content=ErrorResponse(message=ex.message).model_dump(),
            status_code=status.HTTP_404_NOT_FOUND,
        )


@router.delete(
    "/{course_id}",
    status_code=status.HTTP_200_OK,
    description="Delete course",
    summary="Delete course",
    responses={
        status.HTTP_200_OK: {
            "model": SuccessResponse,
            "description": "Course deleted",
        },
        status.HTTP_404_NOT_FOUND: {
            "model": ErrorResponse,
            "description": "No course",
        },
    },
    response_model=SuccessResponse,
)
async def delete_course(
    course_id: str = Path(),
    _: UserEntity = Depends(get_admin),
    command_service: CourseCommandService = Depends(get_courses_command_service),
    admin_query_service: AdminCourseQueryService = Depends(get_admin_courses_query_service),
    talent_query_service: TalentCourseQueryService = Depends(get_talent_courses_query_service),
) -> JSONResponse:
    """Create course.

    :param talent_query_service:
    :param admin_query_service:
    :param _:
    :param course_id:
    :param command_service:
    :return:
    """
    try:
        await command_service.delete_course(course_id)
        await admin_query_service.invalidate_course(course_id)
        await talent_query_service.invalidate_course(course_id)
        return JSONResponse(
            content=SuccessResponse(message="Course has deleted").model_dump(),
            status_code=status.HTTP_200_OK,
        )
    except CourseNotFoundError as ex:
        return JSONResponse(
            content=ErrorResponse(message=ex.message).model_dump(),
            status_code=status.HTTP_404_NOT_FOUND,
        )


@router.get(
    "/{course_id}",
    status_code=status.HTTP_200_OK,
    description="Get course",
    summary="Get course",
    responses={
        status.HTTP_200_OK: {
            "model": SuccessResponse,
            "description": "Course deleted",
        },
        status.HTTP_404_NOT_FOUND: {
            "model": ErrorResponse,
            "description": "No course",
        },
    },
    response_model=SuccessResponse,
)
async def get_course(
    course_id: str = Path(),
    _: UserEntity = Depends(get_admin),
    query_service: AdminCourseQueryService = Depends(get_admin_courses_query_service),
) -> JSONResponse:
    """Get course.

    :param _:
    :param course_id:
    :param query_service:
    :return:
    """
    try:
        course = await query_service.get_course(course_id)
        return JSONResponse(
            content=CourseFullDTO.from_domain(course).model_dump(),
            status_code=status.HTTP_200_OK,
        )
    except CourseNotFoundError as ex:
        return JSONResponse(
            content=ErrorResponse(message=ex.message).model_dump(),
            status_code=status.HTTP_404_NOT_FOUND,
        )


@router.get(
    "",
    status_code=status.HTTP_200_OK,
    description="Get all courses",
    summary="Get courses",
    responses={
        status.HTTP_200_OK: {
            "model": list[CourseShortDTO],
            "description": "All courses",
        },
    },
    response_model=list[CourseShortDTO],
)
async def get_courses(
    _: UserEntity = Depends(get_admin),
    query_service: AdminCourseQueryService = Depends(get_admin_courses_query_service),
) -> list[CourseShortDTO]:
    """Get courses.

    :param _:
    :param query_service:
    :return:
    """
    courses = await query_service.get_courses()
    return [CourseShortDTO.from_domain(course) for course in courses]


@router.post(
    "/{course_id}/published",
    status_code=status.HTTP_200_OK,
    description="Publish course",
    summary="Publish course",
    responses={
        status.HTTP_200_OK: {
            "model": SuccessResponse,
            "description": "Course published",
        },
        status.HTTP_404_NOT_FOUND: {
            "model": ErrorResponse,
            "description": "No course",
        },
        status.HTTP_409_CONFLICT: {
            "model": ErrorResponse,
            "description": "No course",
        },
    },
    response_model=SuccessResponse,
)
async def publish_course(
    course_id: str = Path(),
    _: UserEntity = Depends(get_admin),
    command_service: CourseCommandService = Depends(get_courses_command_service),
    admin_query_service: AdminCourseQueryService = Depends(get_admin_courses_query_service),
    talent_query_service: TalentCourseQueryService = Depends(get_talent_courses_query_service),
) -> JSONResponse:
    """Publish course.

    :param talent_query_service:
    :param admin_query_service:
    :param _:
    :param course_id:
    :param command_service:
    :return:
    """
    try:
        await command_service.publish_course(course_id)
        await admin_query_service.invalidate_course(course_id)
        await talent_query_service.invalidate_course(course_id)
        return JSONResponse(
            content=SuccessResponse(message="Course has published").model_dump(),
            status_code=status.HTTP_200_OK,
        )
    except CourseNotFoundError as ex:
        return JSONResponse(
            content=ErrorResponse(message=ex.message).model_dump(),
            status_code=status.HTTP_404_NOT_FOUND,
        )
    except CoursePublishError as ex:
        return JSONResponse(
            content=ErrorResponse(message=ex.message).model_dump(),
            status_code=status.HTTP_409_CONFLICT,
        )


@router.delete(
    "/{course_id}/published",
    status_code=status.HTTP_200_OK,
    description="Hide course",
    summary="Hide course",
    responses={
        status.HTTP_200_OK: {
            "model": SuccessResponse,
            "description": "Course unpublished",
        },
        status.HTTP_404_NOT_FOUND: {
            "model": ErrorResponse,
            "description": "No course",
        },
        status.HTTP_409_CONFLICT: {
            "model": ErrorResponse,
            "description": "No course",
        },
    },
    response_model=SuccessResponse,
)
async def hide_course(
    course_id: str = Path(),
    _: UserEntity = Depends(get_admin),
    command_service: CourseCommandService = Depends(get_courses_command_service),
    admin_query_service: AdminCourseQueryService = Depends(get_admin_courses_query_service),
    talent_query_service: TalentCourseQueryService = Depends(get_talent_courses_query_service),
) -> JSONResponse:
    """Hide/unpublish course.

    :param talent_query_service:
    :param admin_query_service:
    :param _:
    :param course_id:
    :param command_service:
    :return:
    """
    try:
        await command_service.hide_course(course_id)
        await admin_query_service.invalidate_course(course_id)
        await talent_query_service.invalidate_course(course_id)
        return JSONResponse(
            content=SuccessResponse(message="Course has unpublished").model_dump(),
            status_code=status.HTTP_200_OK,
        )
    except CourseNotFoundError as ex:
        return JSONResponse(
            content=ErrorResponse(message=ex.message).model_dump(),
            status_code=status.HTTP_404_NOT_FOUND,
        )
    except CoursePublishError as ex:
        return JSONResponse(
            content=ErrorResponse(message=ex.message).model_dump(),
            status_code=status.HTTP_409_CONFLICT,
        )

===== END FILE =====

===== FILE: src/api/admin/courses/schemas.py =====
from __future__ import annotations

from pydantic import BaseModel, Field

from src.api.courses.schemas import ResourceDTO


class CreateCourseRequest(BaseModel):

    """Schema of course."""

    name: str = Field("NoSQL")


class CreateCourseResponse(BaseModel):

    """Schema of course."""

    course_id: str = Field("fsf4r6srr6s8f4fs")


class UpdateCourseRequest(BaseModel):

    """Schema of course."""

    name: str = Field("NoSQL")
    image_url: str | None = Field("image/path-to-file.png")
    limits: int | None = Field(25)

    prerequisites: str | None = Field("SQL, Basic RDBMS")
    description: str | None = Field("Information about NoSQL")
    topics: str | None = Field("1. History of NoSQL, 2. MongoDB, 3. Cassandra")
    assessment: str | None = Field("The capstone project")
    resources: list[ResourceDTO] = Field([ResourceDTO(title="Полезная книга", link="Ссылка на книгу")])
    extra: str | None = Field("")

    author: str | None = Field("Иванов И. И.")
    implementer: str | None = Field("ИПКН")
    format: str | None = Field("online-курс")
    terms: str | None = Field("1, 3")
    roles: list[str] = Field(["AI Product Manager"])
    periods: list[str] = Field(["сентябрь", "октябрь"])
    last_runs: list[str] = Field(["Весна 2023"])

===== END FILE =====

===== FILE: src/api/admin/group_google_calendar/__init__.py =====

===== END FILE =====

===== FILE: src/api/admin/group_google_calendar/dependencies.py =====
from __future__ import annotations

from typing import TYPE_CHECKING

from fastapi import Depends

from src.infrastructure.sqlalchemy.group_google_calendar.unit_of_work import SQLAlchemyGGCUnitOfWork
from src.infrastructure.sqlalchemy.session import get_async_session
from src.services.group_google_calendar.command_service import GroupGoogleCalendarCommandService

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


def get_group_google_calendar_service(
        db_session: AsyncSession = Depends(get_async_session),
) -> GroupGoogleCalendarCommandService:
    """Get group google calendar service on sessions.

    :param db_session:
    :return:
    """
    unit_of_work = SQLAlchemyGGCUnitOfWork(db_session)
    return GroupGoogleCalendarCommandService(unit_of_work)

===== END FILE =====

===== FILE: src/api/admin/group_google_calendar/integration_router.py =====
from fastapi import APIRouter, Body, Depends, status
from fastapi.responses import JSONResponse

from src.api.admin.courses.dependencies import get_admin
from src.api.admin.group_google_calendar.dependencies import get_group_google_calendar_service
from src.api.admin.group_google_calendar.schemas import (
    UpdateCourseGroupGoogleCalendarMessageResponse,
    UpdateCourseGroupGoogleCalendarsRequest,
)
from src.domain.auth.entities import UserEntity
from src.services.group_google_calendar.command_service import GroupGoogleCalendarCommandService
from src.services.group_google_calendar.dto import UpdateGroupDTO, UpdateGroupGoogleCalendarDTO

router = APIRouter(prefix="/integrations/google_calendar_links", tags=["integrations"])


@router.post(
    "",
    status_code=status.HTTP_200_OK,
    description="Add google calendar links for one course. The group name is optional, it is required if there is "
                "more than one group",
    summary="Add google calendar links",
    responses={
        status.HTTP_200_OK: {
            "model": UpdateCourseGroupGoogleCalendarMessageResponse,
            "description": "Messages explained processing. OK is standard message after success processing",
        },
    },
    response_model=UpdateCourseGroupGoogleCalendarMessageResponse,
)
async def update_google_calendar_links(
    _: UserEntity = Depends(get_admin),
    data: UpdateCourseGroupGoogleCalendarsRequest = Body(),
    command_service: GroupGoogleCalendarCommandService = Depends(get_group_google_calendar_service),
) -> JSONResponse:
    """Update google calendar links.

    :return:
    """
    course = UpdateGroupGoogleCalendarDTO(
        course_name=data.course.name,
        groups=[UpdateGroupDTO(name=g.name, link=g.link) for g in data.course.groups],
    )
    message = await command_service.update(course, data.course_run_name)
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=UpdateCourseGroupGoogleCalendarMessageResponse(message=message).model_dump(mode="json"),
    )

===== END FILE =====

===== FILE: src/api/admin/group_google_calendar/router.py =====
from fastapi import APIRouter, Body, Depends, status
from fastapi.responses import JSONResponse

from src.api.admin.courses.dependencies import get_admin
from src.api.admin.group_google_calendar.dependencies import get_group_google_calendar_service
from src.api.admin.group_google_calendar.schemas import CreateGroupGoogleCalendarRequest
from src.api.base_schemas import ErrorResponse, SuccessResponse
from src.api.timetable.schemas import GroupGoogleCalendarDTO
from src.domain.auth.entities import UserEntity
from src.domain.base_exceptions import InvalidLinkError
from src.domain.group_google_calendar.exceptions import GroupGoogleCalendarNotFoundError
from src.services.group_google_calendar.command_service import GroupGoogleCalendarCommandService

router = APIRouter(
    prefix="/admin/courses/{course_id}/runs/{course_run_id}/timetable/google_calendar_groups",
    tags=["admin"],
)


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    description="Create google calendar link",
    summary="Create google calendar link",
    responses={
        status.HTTP_201_CREATED: {
            "model": SuccessResponse,
            "description": "Google calendar has been created",
        },
        status.HTTP_422_UNPROCESSABLE_ENTITY: {
            "model": ErrorResponse,
            "description": "Invalid data",
        },
    },
    response_model=SuccessResponse,
)
async def create_group_google_calendar(
    course_id: str,
    course_run_id: str,
    data: CreateGroupGoogleCalendarRequest = Body(),
    _: UserEntity = Depends(get_admin),
    command_service: GroupGoogleCalendarCommandService = Depends(get_group_google_calendar_service),
) -> JSONResponse:
    """Create google calendar link.

    :return:
    """
    try:
        await command_service.create(course_run_id, data.name, data.link)
        return JSONResponse(
            status_code=status.HTTP_201_CREATED,
            content=SuccessResponse(message="Ссылка на google calendar успешно создана").model_dump(mode="json"),
        )
    except InvalidLinkError as ex:
        return JSONResponse(
            content=ErrorResponse(message=ex.message).model_dump(),
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        )


@router.get(
    "",
    status_code=status.HTTP_200_OK,
    description="Get google calendar links by course run",
    summary="Get google calendar links",
    responses={
        status.HTTP_200_OK: {
            "model": list[GroupGoogleCalendarDTO],
            "description": "Google calendar has been deleted",
        },
    },
    response_model=list[GroupGoogleCalendarDTO],
)
async def get_group_google_calendars(
    course_id: str,
    course_run_id: str,
    _: UserEntity = Depends(get_admin),
    command_service: GroupGoogleCalendarCommandService = Depends(get_group_google_calendar_service),
) -> JSONResponse:
    """Get google calendar links.

    :return:
    """
    groups = await command_service.get_groups(course_run_id)
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=[GroupGoogleCalendarDTO.from_domain(g).model_dump(mode="json") for g in groups],
    )


@router.delete(
    "/{group_google_calendar_id}",
    status_code=status.HTTP_200_OK,
    description="Delete google calendar link",
    summary="Delete google calendar link",
    responses={
        status.HTTP_200_OK: {
            "model": SuccessResponse,
            "description": "Google calendar has been deleted",
        },
        status.HTTP_404_NOT_FOUND: {
            "model": ErrorResponse,
            "description": "Google calendar has been created",
        },
    },
    response_model=SuccessResponse,
)
async def delete_group_google_calendar(
    course_id: str,
    course_run_id: str,
    group_google_calendar_id: str,
    _: UserEntity = Depends(get_admin),
    command_service: GroupGoogleCalendarCommandService = Depends(get_group_google_calendar_service),
) -> JSONResponse:
    """Delete google calendar link.

    :return:
    """
    try:
        await command_service.delete(group_google_calendar_id)
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=SuccessResponse(message="Ссылка на google calendar успешно удалена").model_dump(mode="json"),
        )
    except GroupGoogleCalendarNotFoundError as ex:
        return JSONResponse(
            content=ErrorResponse(message=ex.message).model_dump(),
            status_code=status.HTTP_404_NOT_FOUND,
        )

===== END FILE =====

===== FILE: src/api/admin/group_google_calendar/schemas.py =====
from __future__ import annotations

from typing import TYPE_CHECKING

from pydantic import BaseModel, Field

if TYPE_CHECKING:
    from src.domain.group_google_calendar.entities import GroupGoogleCalendarEntity


class GroupGoogleCalendarDTO(BaseModel):

    """Schema for group google calendar."""

    id: str
    name: str
    link: str

    @staticmethod
    def from_domain(group: GroupGoogleCalendarEntity) -> GroupGoogleCalendarDTO:
        return GroupGoogleCalendarDTO(
            id=group.id.value,
            name=group.name,
            link=group.link.value,
        )


class CreateGroupGoogleCalendarRequest(BaseModel):

    """Schema for creating group google calendar."""

    name: str
    link: str


class UpdateCourseGroupGoogleCalendarsRequest(BaseModel):

    """Schema-request for updating one group google calendars."""

    course_run_name: str = Field("Осень 2024")
    course: CourseDTO


class UpdateCourseGroupGoogleCalendarMessageResponse(BaseModel):

    """Schema-response for updating one group google calendars."""

    message: str = Field("OK")


class CourseDTO(BaseModel):

    """Schema of course for updating google calendar groups."""

    name: str = Field("A/B тестирование")
    groups: list[CourseGroupDTO]


class CourseGroupDTO(BaseModel):

    """Schema of certain google calendar group."""

    name: str = Field("Группа в 17:00")
    link: str = Field("https://calendar.google.com/calendar/...")

===== END FILE =====

===== FILE: src/api/admin/playlists/__init__.py =====

===== END FILE =====

===== FILE: src/api/admin/playlists/dependencies.py =====
from __future__ import annotations

from typing import TYPE_CHECKING

from fastapi import Depends

from src.infrastructure.sqlalchemy.playlists.unit_of_work import SQLAlchemyPlaylistUnitOfWork
from src.infrastructure.sqlalchemy.session import get_async_session
from src.services.playlists.command_service import PlaylistCommandService

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


def get_playlist_service(
        db_session: AsyncSession = Depends(get_async_session),
) -> PlaylistCommandService:
    """Get playlist service on sessions.

    :param db_session:
    :return:
    """
    unit_of_work = SQLAlchemyPlaylistUnitOfWork(db_session)
    return PlaylistCommandService(unit_of_work)

===== END FILE =====

===== FILE: src/api/admin/playlists/router.py =====
from fastapi import APIRouter, Body, Depends, status
from fastapi.responses import JSONResponse

from src.api.admin.courses.dependencies import get_admin
from src.api.admin.playlists.dependencies import get_playlist_service
from src.api.admin.playlists.schemas import CreateOrUpdatePlaylistRequest, PlaylistDTO
from src.api.base_schemas import ErrorResponse, SuccessResponse
from src.domain.auth.entities import UserEntity
from src.domain.base_exceptions import InvalidLinkError
from src.domain.courses.exceptions import ValueDoesntExistError
from src.domain.playlists.exceptions import PlaylistNotFoundError
from src.services.playlists.command_service import PlaylistCommandService

router = APIRouter(
    prefix="/admin/courses/{course_id}/runs/{course_run_id}/playlists",
    tags=["admin"],
)


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    description="Create playlist",
    summary="Create playlist",
    responses={
        status.HTTP_201_CREATED: {
            "model": SuccessResponse,
            "description": "Playlist has been created",
        },
        status.HTTP_422_UNPROCESSABLE_ENTITY: {
            "model": ErrorResponse,
            "description": "Invalid data",
        },
    },
    response_model=SuccessResponse,
)
async def create_group_google_calendar(
    course_id: str,
    course_run_id: str,
    data: CreateOrUpdatePlaylistRequest = Body(),
    _: UserEntity = Depends(get_admin),
    command_service: PlaylistCommandService = Depends(get_playlist_service),
) -> JSONResponse:
    """Create playlist.

    :return:
    """
    try:
        await command_service.create_playlist(course_run_id, data.name, data.type, data.link)
        return JSONResponse(
            status_code=status.HTTP_201_CREATED,
            content=SuccessResponse(message="Плейлист успешно создан").model_dump(mode="json"),
        )
    except (InvalidLinkError, ValueDoesntExistError) as ex:
        return JSONResponse(
            content=ErrorResponse(message=ex.message).model_dump(),
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        )


@router.get(
    "",
    status_code=status.HTTP_200_OK,
    description="Get playlists by course run",
    summary="Get playlists",
    responses={
        status.HTTP_200_OK: {
            "model": list[PlaylistDTO],
            "description": "Playlists",
        },
    },
    response_model=list[PlaylistDTO],
)
async def get_playlists(
    course_id: str,
    course_run_id: str,
    _: UserEntity = Depends(get_admin),
    command_service: PlaylistCommandService = Depends(get_playlist_service),
) -> JSONResponse:
    """Get google calendar links.

    :return:
    """
    playlists = await command_service.get_playlists_by_course_run_id(course_run_id)
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=[PlaylistDTO.from_domain(p).model_dump(mode="json") for p in playlists],
    )


@router.delete(
    "/{playlist_id}",
    status_code=status.HTTP_200_OK,
    description="Delete playlist",
    summary="Delete playlist",
    responses={
        status.HTTP_200_OK: {
            "model": SuccessResponse,
            "description": "Playlist has been deleted",
        },
        status.HTTP_404_NOT_FOUND: {
            "model": ErrorResponse,
            "description": "No such playlist",
        },
    },
    response_model=SuccessResponse,
)
async def delete_playlist(
    course_id: str,
    course_run_id: str,
    playlist_id: str,
    _: UserEntity = Depends(get_admin),
    command_service: PlaylistCommandService = Depends(get_playlist_service),
) -> JSONResponse:
    """Delete playlist.

    :return:
    """
    try:
        await command_service.delete_playlist(playlist_id)
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=SuccessResponse(message="Плейлист успешно удален").model_dump(mode="json"),
        )
    except PlaylistNotFoundError as ex:
        return JSONResponse(
            content=ErrorResponse(message=ex.message).model_dump(),
            status_code=status.HTTP_404_NOT_FOUND,
        )


@router.put(
    "/{playlist_id}",
    status_code=status.HTTP_200_OK,
    description="Update playlist",
    summary="Update playlist",
    responses={
        status.HTTP_200_OK: {
            "model": SuccessResponse,
            "description": "Playlist has been updated",
        },
        status.HTTP_404_NOT_FOUND: {
            "model": ErrorResponse,
            "description": "No such playlist",
        },
        status.HTTP_422_UNPROCESSABLE_ENTITY: {
            "model": ErrorResponse,
            "description": "Invalid data",
        },
    },
    response_model=SuccessResponse,
)
async def update_playlist(
    course_id: str,
    course_run_id: str,
    playlist_id: str,
    data: CreateOrUpdatePlaylistRequest = Body(),
    _: UserEntity = Depends(get_admin),
    command_service: PlaylistCommandService = Depends(get_playlist_service),
) -> JSONResponse:
    """Update playlist.

    :return:
    """
    try:
        await command_service.update_playlist(playlist_id, course_run_id, data.name, data.type, data.link)
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=SuccessResponse(message="Плейлист успешно обновлен").model_dump(mode="json"),
        )
    except PlaylistNotFoundError as ex:
        return JSONResponse(
            content=ErrorResponse(message=ex.message).model_dump(),
            status_code=status.HTTP_404_NOT_FOUND,
        )
    except (InvalidLinkError, ValueDoesntExistError) as ex:
        return JSONResponse(
            content=ErrorResponse(message=ex.message).model_dump(),
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        )

===== END FILE =====

===== FILE: src/api/admin/playlists/schemas.py =====
from __future__ import annotations

from typing import TYPE_CHECKING

from pydantic import BaseModel

if TYPE_CHECKING:
    from src.domain.playlists.entities import PlaylistEntity


class PlaylistDTO(BaseModel):

    """Schema for playlist."""

    id: str
    name: str
    type: str
    link: str

    @staticmethod
    def from_domain(playlist: PlaylistEntity) -> PlaylistDTO:
        return PlaylistDTO(
            id=playlist.id.value,
            name=playlist.name,
            type=playlist.type.value,
            link=playlist.link.value,
        )


class CreateOrUpdatePlaylistRequest(BaseModel):

    """Schema for creating or updating playlist."""

    name: str
    type: str
    link: str

===== END FILE =====

===== FILE: src/api/admin/timetable/__init__.py =====

===== END FILE =====

===== FILE: src/api/admin/timetable/dependencies.py =====
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.infrastructure.sqlalchemy.session import get_async_session
from src.infrastructure.sqlalchemy.timetable.unit_of_work import SQLAlchemyTimetableUnitOfWork
from src.services.timetable.command_service import TimetableCommandService


def get_admin_timetable_command_service(
    db_session: AsyncSession = Depends(get_async_session),
) -> TimetableCommandService:
    """Get feedback service on sessions.

    :param db_session:
    :return:
    """
    unit_of_work = SQLAlchemyTimetableUnitOfWork(db_session)
    return TimetableCommandService(unit_of_work)

===== END FILE =====

===== FILE: src/api/admin/timetable/router.py =====
from fastapi import APIRouter, Body, Depends, status
from fastapi.responses import JSONResponse

from src.api.admin.courses.dependencies import get_admin
from src.api.admin.timetable.dependencies import get_admin_timetable_command_service
from src.api.admin.timetable.schemas import CreateOrUpdateRuleRequest, CreateRuleResponse, TimetableDTO
from src.api.base_schemas import ErrorResponse, SuccessResponse
from src.domain.auth.entities import UserEntity
from src.domain.timetable.exceptions import IncorrectRuleTypeError, RuleNotFoundError
from src.services.timetable.command_service import TimetableCommandService

router = APIRouter(prefix="/admin/courses/{course_id}/runs/{course_run_id}/timetable", tags=["admin"])


@router.get(
    "",
    status_code=status.HTTP_200_OK,
    description="Get timetable for course run",
    summary="Get timetable",
    responses={
        status.HTTP_200_OK: {
            "model": TimetableDTO,
            "description": "Get timetable",
        },
        status.HTTP_404_NOT_FOUND: {
            "model": ErrorResponse,
            "description": "Error",
        },
    },
    response_model=TimetableDTO,
)
async def get_timetable(
    course_id: str,
    course_run_id: str,
    _: UserEntity = Depends(get_admin),
    command_service: TimetableCommandService = Depends(get_admin_timetable_command_service),
) -> JSONResponse:
    """Get timetable.

    :return:
    """
    timetable = await command_service.get_timetable_by_course_run_id(course_run_id)
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=TimetableDTO.from_domain(timetable).model_dump(mode="json"),
    )


@router.post(
    "/rules",
    status_code=status.HTTP_201_CREATED,
    description="Create rule",
    summary="Create rule",
    responses={
        status.HTTP_201_CREATED: {
            "model": CreateRuleResponse,
            "description": "Rule has been created",
        },
        status.HTTP_422_UNPROCESSABLE_ENTITY: {
            "model": ErrorResponse,
            "description": "Validation error",
        },
    },
    response_model=CreateRuleResponse,
)
async def create_rule(
    course_id: str,
    course_run_id: str,
    data: CreateOrUpdateRuleRequest = Body(),
    _: UserEntity = Depends(get_admin),
    command_service: TimetableCommandService = Depends(get_admin_timetable_command_service),
) -> JSONResponse:
    """Create rule.

    :return:
    """
    try:
        if data.type == "day":
            rule_id = await command_service.create_day_rule(
                course_run_id, data.rule.start_time, data.rule.end_time, data.rule.date,
            )
        elif data.type == "week":
            rule_id = await command_service.create_week_rule(
                course_run_id, data.rule.start_time, data.rule.end_time,
                data.rule.start_period_date, data.rule.end_period_date, data.rule.weekdays,
            )
        else:
            return JSONResponse(
                content=ErrorResponse(message=IncorrectRuleTypeError().message).model_dump(),
                status_code=status.HTTP_404_NOT_FOUND,
            )
        return JSONResponse(
            status_code=status.HTTP_201_CREATED,
            content=CreateRuleResponse(rule_id=rule_id).model_dump(),
        )
    except (AttributeError, IncorrectRuleTypeError):
        return JSONResponse(
            content=ErrorResponse(message=IncorrectRuleTypeError().message).model_dump(),
            status_code=status.HTTP_404_NOT_FOUND,
        )


@router.delete(
    "/rules/{rule_id}",
    status_code=status.HTTP_200_OK,
    description="Delete rule",
    summary="Delete rule",
    responses={
        status.HTTP_200_OK: {
            "model": SuccessResponse,
            "description": "Rule run has been deleted",
        },
        status.HTTP_404_NOT_FOUND: {
            "model": ErrorResponse,
            "description": "Error",
        },
    },
    response_model=SuccessResponse,
)
async def delete_rule(
    course_id: str,
    course_run_id: str,
    rule_id: str,
    _: UserEntity = Depends(get_admin),
    command_service: TimetableCommandService = Depends(get_admin_timetable_command_service),
) -> JSONResponse:
    """Delete rule.

    :return:
    """
    try:
        await command_service.delete_rule(rule_id)
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=SuccessResponse(message="Правило успешно удалено").model_dump(),
        )
    except RuleNotFoundError as ex:
        return JSONResponse(
            content=ErrorResponse(message=ex.message).model_dump(),
            status_code=status.HTTP_404_NOT_FOUND,
        )


@router.put(
    "/rules/{rule_id}",
    status_code=status.HTTP_200_OK,
    description="Update rule",
    summary="Update rule",
    responses={
        status.HTTP_200_OK: {
            "model": SuccessResponse,
            "description": "Rule run has been updated",
        },
        status.HTTP_404_NOT_FOUND: {
            "model": ErrorResponse,
            "description": "Error",
        },
        status.HTTP_422_UNPROCESSABLE_ENTITY: {
            "model": ErrorResponse,
            "description": "Error",
        },
    },
    response_model=SuccessResponse,
)
async def update_rule(
    course_id: str,
    course_run_id: str,
    rule_id: str,
    data: CreateOrUpdateRuleRequest = Body(),
    _: UserEntity = Depends(get_admin),
    command_service: TimetableCommandService = Depends(get_admin_timetable_command_service),
) -> JSONResponse:
    """Update rule.

    :return:
    """
    try:
        if data.type == "day":
            await command_service.update_day_rule(
                rule_id, course_run_id, data.rule.start_time, data.rule.end_time, data.rule.date,
            )
        elif data.type == "week":
            await command_service.update_week_rule(
                rule_id, course_run_id, data.rule.start_time, data.rule.end_time,
                data.rule.start_period_date, data.rule.end_period_date, data.rule.weekdays,
            )
        else:
            return JSONResponse(
                content=ErrorResponse(message=IncorrectRuleTypeError().message).model_dump(),
                status_code=status.HTTP_404_NOT_FOUND,
            )
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=SuccessResponse(message="Правило успешно обновлено").model_dump(),
        )
    except RuleNotFoundError as ex:
        return JSONResponse(
            content=ErrorResponse(message=ex.message).model_dump(),
            status_code=status.HTTP_404_NOT_FOUND,
        )
    except (AttributeError, IncorrectRuleTypeError):
        return JSONResponse(
            content=ErrorResponse(message=IncorrectRuleTypeError().message).model_dump(),
            status_code=status.HTTP_404_NOT_FOUND,
        )

===== END FILE =====

===== FILE: src/api/admin/timetable/schemas.py =====
from __future__ import annotations

import datetime
from typing import Literal

from pydantic import BaseModel

from src.domain.timetable.entities import DayRuleEntity, TimetableEntity, WeekRuleEntity


class DayRuleDTO(BaseModel):

    """Schema for day rule."""

    id: str
    timetable_id: str
    type: str
    start_time: datetime.time
    end_time: datetime.time
    date: datetime.date

    @staticmethod
    def from_domain(rule: DayRuleEntity) -> DayRuleDTO:
        return DayRuleDTO(
            id=rule.id.value,
            timetable_id=rule.timetable_id.value,
            type="day",
            start_time=rule.start_time,
            end_time=rule.end_time,
            date=rule.date,
        )


class CreateOrUpdateRuleDayDTO(BaseModel):

    """Schema for create or update day rule."""

    start_time: datetime.time
    end_time: datetime.time
    date: datetime.date


class WeekRuleDTO(BaseModel):

    """Schema for week rule."""

    id: str
    timetable_id: str
    type: str
    start_time: datetime.time
    end_time: datetime.time
    start_period_date: datetime.date
    end_period_date: datetime.date
    weekdays: list[str]

    @staticmethod
    def from_domain(rule: WeekRuleEntity) -> WeekRuleDTO:
        return WeekRuleDTO(
            id=rule.id.value,
            timetable_id=rule.timetable_id.value,
            type="week",
            start_time=rule.start_time,
            end_time=rule.end_time,
            start_period_date=rule.start_period_date,
            end_period_date=rule.end_period_date,
            weekdays=[w.value for w in rule.weekdays],
        )


class CreateOrUpdateWeekRuleDTO(BaseModel):

    """Schema for create or update week rule."""

    start_time: datetime.time
    end_time: datetime.time
    start_period_date: datetime.date
    end_period_date: datetime.date
    weekdays: list[str]


class CreateRuleResponse(BaseModel):

    """Schema of create rule response."""

    rule_id: str


class CreateOrUpdateRuleRequest(BaseModel):

    """Schema of create or update rule request."""

    type: Literal["day", "week"]
    rule: CreateOrUpdateRuleDayDTO | CreateOrUpdateWeekRuleDTO


class LessonDTO(BaseModel):

    """Schema of lesson."""

    start_time: datetime.time
    end_time: datetime.time
    date: datetime.date
    warning_messages: list[str]


class TimetableDTO(BaseModel):

    """Schema of timetable."""

    id: str
    rules: list[DayRuleDTO | WeekRuleDTO]
    lessons: list[LessonDTO]

    @staticmethod
    def from_domain(timetable: TimetableEntity) -> TimetableDTO:
        current_lessons = timetable.lessons
        warnings = timetable.warnings
        return TimetableDTO(
            id=timetable.id.value,
            lessons=[
                LessonDTO(
                    start_time=lesson.start_time.time(),
                    end_time=lesson.end_time.time(),
                    date=lesson.start_time.date(),
                    warning_messages=[w.message for w in warnings if w.day == lesson.start_time.date()],
                ) for lesson in current_lessons
            ],
            rules=[
                (WeekRuleDTO.from_domain(rule) if isinstance(rule, WeekRuleEntity) else DayRuleDTO.from_domain(rule))
                for rule in timetable.rules
            ],
        )

===== END FILE =====

===== FILE: src/api/auth/__init__.py =====

===== END FILE =====

===== FILE: src/api/auth/dependencies.py =====
from __future__ import annotations

from typing import TYPE_CHECKING

from fastapi import Depends, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from src.domain.auth.exceptions import UserBySessionNotFoundError
from src.exceptions import ApplicationError
from src.infrastructure.redis.auth.session_service import RedisSessionService
from src.infrastructure.redis.session import get_redis_session
from src.infrastructure.sqlalchemy.session import get_async_session
from src.infrastructure.sqlalchemy.users.unit_of_work import SQLAlchemyAuthUnitOfWork
from src.services.auth.command_service import AuthCommandService

if TYPE_CHECKING:
    from redis.asyncio import Redis
    from sqlalchemy.ext.asyncio import AsyncSession

    from src.domain.auth.entities import UserEntity


def get_auth_service(
        db_session: AsyncSession = Depends(get_async_session),
        cache_session: Redis = Depends(get_redis_session),
) -> AuthCommandService:
    """Get auth service on sessions.

    :param db_session:
    :param cache_session:
    :return:
    """
    unit_of_work = SQLAlchemyAuthUnitOfWork(db_session)
    session_service = RedisSessionService(cache_session)
    return AuthCommandService(unit_of_work, session_service)


def get_auth_token(credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer(auto_error=False))) -> str:
    """Get auth token from header.

    :param credentials:
    :return:
    """
    if not credentials:
        raise ApplicationError(
            message="Требуется войти в аккаунт",
            status=status.HTTP_401_UNAUTHORIZED,
        )
    return credentials.credentials


async def get_user(
        auth_token: str = Depends(get_auth_token),
        auth_service: AuthCommandService = Depends(get_auth_service),
) -> UserEntity:
    """Get user on auth token.

    :param auth_token:
    :param auth_service:
    :return:
    """
    try:
        return await auth_service.me(auth_token)
    except UserBySessionNotFoundError as ex:
        raise ApplicationError(
            message="Требуется перезайти в аккаунт",
            status=status.HTTP_401_UNAUTHORIZED,
        ) from ex


async def get_user_or_anonym(
        credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer(auto_error=False)),
        auth_service: AuthCommandService = Depends(get_auth_service),
) -> UserEntity | None:
    """Get user on auth token or anonym.

    :param credentials:
    :param auth_service:
    :return:
    """
    anonym = None
    try:
        if not credentials:
            return anonym
        return await auth_service.me(credentials.credentials)
    except UserBySessionNotFoundError:
        return anonym

===== END FILE =====

===== FILE: src/api/auth/router.py =====
from fastapi import APIRouter, Depends, status
from starlette.responses import JSONResponse

from src.api.auth.dependencies import get_auth_service, get_auth_token, get_user
from src.api.auth.schemas import (
    AuthTokenResponse,
    LoginRequest,
    RegisterRequest,
    UserDTO,
)
from src.api.base_schemas import ErrorResponse, SuccessResponse
from src.domain.auth.entities import UserEntity
from src.domain.auth.exceptions import (
    EmailNotValidError,
    EmptyPartOfNameError,
    PasswordTooShortError,
    UserNotFoundError,
    UserWithEmailExistsError,
    WrongPasswordError,
)
from src.services.auth.command_service import AuthCommandService

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(
    "/register",
    status_code=status.HTTP_201_CREATED,
    description="Register talent in system",
    summary="Registration",
    responses={
        status.HTTP_201_CREATED: {
            "model": AuthTokenResponse,
            "description": "Registration is successful",
        },
        status.HTTP_422_UNPROCESSABLE_ENTITY: {
            "model": ErrorResponse,
            "description": "Validation error",
        },
        status.HTTP_400_BAD_REQUEST: {
            "model": ErrorResponse,
            "description": "Error in registration",
        },
    },
    response_model=AuthTokenResponse,
)
async def register_talent(
    data: RegisterRequest,
    auth_service: AuthCommandService = Depends(get_auth_service),
) -> JSONResponse:
    """Register new user.

    :param data:
    :param auth_service:
    :return:
    """
    try:
        auth_token = await auth_service.register_talent(
            data.firstname, data.lastname, data.email, data.password,
        )
    except (EmailNotValidError, EmptyPartOfNameError, PasswordTooShortError) as ex:
        return JSONResponse(
            content=ErrorResponse(message=ex.message).model_dump(),
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        )
    except UserWithEmailExistsError as ex:
        return JSONResponse(
            content=ErrorResponse(message=ex.message).model_dump(),
            status_code=status.HTTP_400_BAD_REQUEST,
        )
    return JSONResponse(
        content=AuthTokenResponse(auth_token=auth_token).model_dump(),
        status_code=status.HTTP_201_CREATED,
    )


@router.post(
    "/login",
    status_code=status.HTTP_200_OK,
    description="Login user in system",
    summary="Log in",
    responses={
        status.HTTP_200_OK: {
            "model": AuthTokenResponse,
            "description": "Log in is successful",
        },
        status.HTTP_422_UNPROCESSABLE_ENTITY: {
            "model": ErrorResponse,
            "description": "Validation error",
        },
        status.HTTP_400_BAD_REQUEST: {
            "model": ErrorResponse,
            "description": "Error in login",
        },
    },
    response_model=AuthTokenResponse,
)
async def login_user(
    data: LoginRequest,
    auth_service: AuthCommandService = Depends(get_auth_service),
) -> JSONResponse:
    """Login user.

    :param data:
    :param auth_service:
    :return:
    """
    try:
        auth_token = await auth_service.login(
            data.email, data.password,
        )
    except EmailNotValidError as ex:
        return JSONResponse(
            content=ErrorResponse(message=ex.message).model_dump(),
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        )
    except (WrongPasswordError, UserNotFoundError) as ex:
        return JSONResponse(
            content=ErrorResponse(message=ex.message).model_dump(),
            status_code=status.HTTP_400_BAD_REQUEST,
        )
    return JSONResponse(
        content=AuthTokenResponse(auth_token=auth_token).model_dump(),
        status_code=status.HTTP_200_OK,
    )


@router.post(
    "/logout",
    status_code=status.HTTP_200_OK,
    description="Logout user in system",
    summary="Log out",
    responses={
        status.HTTP_200_OK: {
            "model": SuccessResponse,
            "description": "Log out is successful",
        },
    },
    response_model=SuccessResponse,
)
async def logout_user(
    auth_token: str = Depends(get_auth_token),
    auth_service: AuthCommandService = Depends(get_auth_service),
) -> JSONResponse:
    """Logout current user.

    :param auth_token:
    :param auth_service:
    :return:
    """
    await auth_service.logout(auth_token)
    return JSONResponse(
        content=SuccessResponse(message="Log out is successful").model_dump(),
        status_code=status.HTTP_200_OK,
    )


@router.get(
    "/me",
    status_code=status.HTTP_200_OK,
    description="Get current user",
    summary="Getting user",
    responses={
        status.HTTP_200_OK: {
            "model": UserDTO,
            "description": "Getting current user is successful",
        },
        status.HTTP_401_UNAUTHORIZED: {
            "model": ErrorResponse,
            "description": "No session",
        },
    },
    response_model=UserDTO,
)
async def get_current_user(
    user: UserEntity = Depends(get_user),
) -> JSONResponse:
    """Get current user on auth token.

    :param user:
    :return:
    """
    return JSONResponse(
        content=UserDTO.from_entity(user).model_dump(),
        status_code=status.HTTP_200_OK,
    )

===== END FILE =====

===== FILE: src/api/auth/schemas.py =====
from pydantic import BaseModel, Field

from src.domain.auth.entities import UserEntity


class AuthTokenResponse(BaseModel):

    """Schema of auth token."""

    auth_token: str = Field("423fsdf23ffs3a2sd3432sd2fa2fag")


class LoginRequest(BaseModel):

    """Schema of login."""

    email: str = Field("john@mail.com")
    password: str = Field("super-password")


class RegisterRequest(BaseModel):

    """Schema of registration."""

    firstname: str = Field("Johny")
    lastname: str = Field("Stark")
    email: str = Field("john@mail.com")
    password: str = Field("super-password")


class UserDTO(BaseModel):

    """Schema of user."""

    id: str = Field("423fsdf23ffs3a2sd3432sd2fa2fag")
    firstname: str = Field("Johny")
    lastname: str = Field("Stark")
    email: str = Field("john@mail.com")
    role: str = Field("talent")

    @staticmethod
    def from_entity(user: UserEntity) -> "UserDTO":
        return UserDTO(
            id=user.id.value,
            firstname=user.firstname.value,
            lastname=user.lastname.value,
            email=user.email.value,
            role=user.role.value,
        )

===== END FILE =====

===== FILE: src/api/courses/__init__.py =====

===== END FILE =====

===== FILE: src/api/courses/dependencies.py =====
from fastapi import Depends
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from src.infrastructure.redis.courses.course_cache_service import RedisCourseCacheService
from src.infrastructure.redis.session import get_redis_session
from src.infrastructure.sqlalchemy.courses.repository import SQLAlchemyCourseRepository
from src.infrastructure.sqlalchemy.courses.unit_of_work import SQLAlchemyCoursesUnitOfWork
from src.infrastructure.sqlalchemy.session import get_async_session
from src.services.courses.command_service import CourseCommandService
from src.services.courses.query_service_for_talent import TalentCourseQueryService


def get_talent_courses_query_service(
    db_session: AsyncSession = Depends(get_async_session),
    cache_session: Redis = Depends(get_redis_session),
) -> TalentCourseQueryService:
    """Get courses service on sessions for talent.

    :param db_session:
    :param cache_session:
    :return:
    """
    course_repo = SQLAlchemyCourseRepository(db_session)
    course_cache_service = RedisCourseCacheService(cache_session, "talent")
    return TalentCourseQueryService(course_repo, course_cache_service)


def get_courses_command_service(
    db_session: AsyncSession = Depends(get_async_session),
) -> CourseCommandService:
    """Get courses service on sessions.

    :param db_session:
    :return:
    """
    unit_of_work = SQLAlchemyCoursesUnitOfWork(db_session)
    return CourseCommandService(unit_of_work)

===== END FILE =====

===== FILE: src/api/courses/router.py =====
from __future__ import annotations

from typing import TYPE_CHECKING

from fastapi import APIRouter, Depends, Query, status
from fastapi.responses import JSONResponse

from src.api.auth.dependencies import get_user
from src.api.base_pagination import PaginationError, Paginator
from src.api.base_schemas import ErrorResponse
from src.api.courses.dependencies import get_talent_courses_query_service
from src.api.courses.schemas import (
    CourseFavoriteStatusResponse,
    CourseFullDTO,
    CourseShortDTO,
    CoursesPaginationResponse,
)
from src.api.favorite_courses.dependencies import get_favorite_courses_command_service
from src.domain.courses.entities import CourseEntity
from src.domain.courses.exceptions import CourseNotFoundError
from src.services.courses.query_service_for_talent import CourseFilter

if TYPE_CHECKING:
    from src.domain.auth.entities import UserEntity
    from src.services.courses.query_service_for_talent import TalentCourseQueryService
    from src.services.favorite_courses.command_service import FavoriteCoursesCommandService

router = APIRouter(prefix="/courses", tags=["courses"])


@router.get(
    "",
    status_code=status.HTTP_200_OK,
    description="Get all available courses",
    summary="Get courses",
    responses={
        status.HTTP_200_OK: {
            "model": list[CourseShortDTO],
            "description": "All courses",
        },
        status.HTTP_400_BAD_REQUEST: {
            "model": ErrorResponse,
            "description": "Error with page",
        },
    },
    response_model=list[CourseShortDTO],
)
async def get_courses(
        terms: list[str] = Query(None),
        roles: list[str] = Query(None),
        implementers: list[str] = Query(None),
        formats: list[str] = Query(None),
        query: str = Query(None),
        page: int = Query(1),
        *,
        only_actual: bool = Query(default=False),
        query_service: TalentCourseQueryService = Depends(get_talent_courses_query_service),
) -> JSONResponse:
    """Get courses.

    :param only_actual:
    :param page:
    :param terms:
    :param roles:
    :param implementers:
    :param formats:
    :param query:
    :param query_service:
    :return:
    """
    filters = CourseFilter(
        terms=terms, roles=roles, implementers=implementers,
        formats=formats, only_actual=only_actual, query=query,
    )
    courses = await query_service.get_courses(filters)
    paginator = Paginator[CourseEntity](data=courses, page_size=9)
    try:
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=CoursesPaginationResponse(
                courses=[CourseShortDTO.from_domain(course) for course in paginator.get_data_by_page(page)],
                max_page=paginator.pages[-1],
            ).model_dump(),
        )
    except PaginationError as ex:
        return JSONResponse(
            content=ErrorResponse(message=ex.message).model_dump(),
            status_code=status.HTTP_400_BAD_REQUEST,
        )


@router.get(
    "/{course_id}",
    status_code=status.HTTP_200_OK,
    description="Get full information about course",
    summary="Get course",
    responses={
        status.HTTP_200_OK: {
            "model": CourseFullDTO,
            "description": "One course",
        },
        status.HTTP_404_NOT_FOUND: {
            "model": ErrorResponse,
            "description": "No course with this id",
        },
    },
    response_model=CourseFullDTO,
)
async def get_course(
        course_id: str,
        query_service: TalentCourseQueryService = Depends(get_talent_courses_query_service),
) -> JSONResponse:
    """Get courses.

    :param course_id:
    :param query_service:
    :return:
    """
    try:
        course = await query_service.get_course(course_id)
        return JSONResponse(
            content=CourseFullDTO.from_domain(course).model_dump(),
            status_code=status.HTTP_200_OK,
        )
    except CourseNotFoundError as ex:
        return JSONResponse(
            content=ErrorResponse(message=ex.message).model_dump(),
            status_code=status.HTTP_404_NOT_FOUND,
        )


@router.get(
    "/{course_id}/favorite_status",
    status_code=status.HTTP_200_OK,
    description="Get favorite status for course",
    summary="Get favorite status",
    responses={
        status.HTTP_200_OK: {
            "model": CourseFavoriteStatusResponse,
            "description": "One course",
        },
        status.HTTP_404_NOT_FOUND: {
            "model": ErrorResponse,
            "description": "No course with this id",
        },
    },
    response_model=CourseFavoriteStatusResponse,
)
async def get_favorite_status(
        course_id: str,
        user: UserEntity = Depends(get_user),
        favorites_command_service: FavoriteCoursesCommandService = Depends(get_favorite_courses_command_service),
) -> JSONResponse:
    """Get courses.

    :param favorites_command_service:
    :param user:
    :param course_id:
    :return:
    """
    is_favorite = await favorites_command_service.course_in_favorites(course_id, user.id.value)
    return JSONResponse(
        content=CourseFavoriteStatusResponse(is_favorite=is_favorite).model_dump(),
        status_code=status.HTTP_200_OK,
    )

===== END FILE =====

===== FILE: src/api/courses/schemas.py =====
from __future__ import annotations

from typing import TYPE_CHECKING

from pydantic import BaseModel, Field

if TYPE_CHECKING:
    from src.domain.courses.entities import CourseEntity


class ResourceDTO(BaseModel):

    """Schema of resource for course."""

    title: str = Field("Полезная книга")
    link: str = Field("Ссылка на книгу")


class CourseFullDTO(BaseModel):

    """Schema of course."""

    id: str = Field("423fsdf23ffs3a2sd3432sd2fa2fag")
    name: str = Field("NoSQL")
    image_url: str | None = Field("image/path-to-file.png")
    limits: int | None = Field(25)
    is_draft: bool = Field(default=True)

    prerequisites: str | None = Field("SQL, Basic RDBMS")
    description: str | None = Field("Information about NoSQL")
    topics: str | None = Field("1. History of NoSQL, 2. MongoDB, 3. Cassandra")
    assessment: str | None = Field("The capstone project")
    resources: list[ResourceDTO] = Field([ResourceDTO(title="Полезная книга", link="Ссылка на книгу")])
    extra: str | None = Field("")

    author: str | None = Field("Иванов И. И.")
    implementer: str | None = Field("ИПКН")
    format: str | None = Field("онлайн-курс")
    terms: str | None = Field("1, 3")
    roles: list[str] = Field(["AI Product Manager"])
    periods: list[str] = Field(["Сентябрь", "Октябрь"])
    last_runs: list[str] = Field(["Весна 2023"])

    @staticmethod
    def from_domain(course: CourseEntity) -> CourseFullDTO:
        return CourseFullDTO(
            id=course.id.value,
            name=course.name.value,
            image_url=course.image_url,
            limits=course.limits,
            is_draft=course.is_draft,

            prerequisites=course.prerequisites,
            description=course.description,
            topics=course.topics,
            assessment=course.assessment,
            resources=[ResourceDTO(title=res.title, link=res.link) for res in course.resources],
            extra=course.extra,

            author=course.author.value if course.author else None,
            implementer=course.implementer.value if course.implementer else None,
            format=course.format.value if course.format else None,
            terms=course.terms.value if course.terms else None,
            roles=[role.value for role in course.roles],
            periods=[period.value for period in course.periods],
            last_runs=[run.value for run in course.last_runs],
        )


class CourseShortDTO(BaseModel):

    """Schema of course in course list."""

    id: str = Field("423fsdf23ffs3a2sd3432sd2fa2fag")
    name: str = Field("NoSQL")
    image_url: str | None = Field("image/path-to-file.png")
    is_draft: bool = Field(default=True)
    implementer: str | None = Field("ИПКН")
    format: str | None = Field("online-курс")
    roles: list[str] = Field(["AI Product Manager"])
    last_runs: list[str] = Field(["Весна 2023"])

    @staticmethod
    def from_domain(course: CourseEntity) -> CourseShortDTO:
        return CourseShortDTO(
            id=course.id.value,
            name=course.name.value,
            image_url=course.image_url,
            is_draft=course.is_draft,
            implementer=course.implementer.value if course.implementer else None,
            format=course.format.value if course.format else None,
            roles=[role.value for role in course.roles],
            last_runs=[run.value for run in course.last_runs],
        )


class CoursesPaginationResponse(BaseModel):

    """Schema of courses pagination."""

    courses: list[CourseShortDTO]
    max_page: int


class CourseFavoriteStatusResponse(BaseModel):

    """Schema of favorite status."""

    is_favorite: bool

===== END FILE =====

===== FILE: src/api/favorite_courses/__init__.py =====

===== END FILE =====

===== FILE: src/api/favorite_courses/dependencies.py =====
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.infrastructure.sqlalchemy.favorite_courses.unit_of_work import SQLAlchemyFavoritesUnitOfWork
from src.infrastructure.sqlalchemy.session import get_async_session
from src.services.favorite_courses.command_service import FavoriteCoursesCommandService


def get_favorite_courses_command_service(
    db_session: AsyncSession = Depends(get_async_session),
) -> FavoriteCoursesCommandService:
    """Get favorite courses on sessions.

    :param db_session:
    :return:
    """
    unit_of_work = SQLAlchemyFavoritesUnitOfWork(db_session)
    return FavoriteCoursesCommandService(unit_of_work)

===== END FILE =====

===== FILE: src/api/favorite_courses/router.py =====
from __future__ import annotations

from typing import TYPE_CHECKING

from fastapi import APIRouter, Body, Depends, status
from fastapi.responses import JSONResponse

from src.api.auth.dependencies import get_user
from src.api.base_schemas import ErrorResponse, SuccessResponse
from src.api.courses.dependencies import get_talent_courses_query_service
from src.api.favorite_courses.dependencies import get_favorite_courses_command_service
from src.api.favorite_courses.schemas import AddFavoriteCourseRequest, FavoriteCourseDTO
from src.domain.favorite_courses.exceptions import (
    CourseAlreadyExistsInFavoritesError,
    CourseDoesntExistInFavoritesError,
)
from src.services.courses.query_service_for_talent import CourseFilter

if TYPE_CHECKING:
    from src.domain.auth.entities import UserEntity
    from src.services.courses.query_service_for_talent import TalentCourseQueryService
    from src.services.favorite_courses.command_service import FavoriteCoursesCommandService

router = APIRouter(prefix="/talent/profile/favorites", tags=["talent"])


@router.get(
    "",
    status_code=status.HTTP_200_OK,
    description="Get all favorite courses",
    summary="Get favorites",
    responses={
        status.HTTP_200_OK: {
            "model": list[FavoriteCourseDTO],
            "description": "All favorites",
        },
    },
    response_model=list[FavoriteCourseDTO],
)
async def get_favorite_courses(
    user: UserEntity = Depends(get_user),
    favorites_command_service: FavoriteCoursesCommandService = Depends(get_favorite_courses_command_service),
    query_service: TalentCourseQueryService = Depends(get_talent_courses_query_service),
) -> JSONResponse:
    """Get favorite courses.

    :param user:
    :param favorites_command_service:
    :param query_service:
    :return:
    """
    favorites = await favorites_command_service.get_favorite_courses(user.id.value)
    courses = await query_service.get_courses(CourseFilter())
    courses = {course.id: course for course in courses}
    results = []
    for favorite in favorites:
        if favorite.course_id not in courses:
            continue
        favorite_dto = FavoriteCourseDTO.from_domain(courses[favorite.course_id], favorite)
        results.append(favorite_dto.model_dump())
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=results,
    )


@router.delete(
    "/{favorite_course_id}",
    status_code=status.HTTP_200_OK,
    description="Delete course from favorites",
    summary="Delete favorite",
    responses={
        status.HTTP_200_OK: {
            "model": SuccessResponse,
            "description": "Course has been removed from favorites",
        },
        status.HTTP_404_NOT_FOUND: {
            "model": ErrorResponse,
            "description": "No course with this id",
        },
    },
    response_model=SuccessResponse,
)
async def remove_course_from_favorites(
    favorite_course_id: str,
    _: UserEntity = Depends(get_user),
    favorites_command_service: FavoriteCoursesCommandService = Depends(get_favorite_courses_command_service),
) -> JSONResponse:
    """Get courses.

    :param _:
    :param favorite_course_id:
    :param favorites_command_service:
    :return:
    """
    try:
        await favorites_command_service.remove_course_from_favorites(favorite_course_id)
        return JSONResponse(
            content=SuccessResponse(message="Курс успешно убран из избранного").model_dump(),
            status_code=status.HTTP_200_OK,
        )
    except CourseDoesntExistInFavoritesError as ex:
        return JSONResponse(
            content=ErrorResponse(message=ex.message).model_dump(),
            status_code=status.HTTP_404_NOT_FOUND,
        )


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    description="Add to favorites",
    summary="Add favorite course",
    responses={
        status.HTTP_201_CREATED: {
            "model": SuccessResponse,
            "description": "Course has been added to favorites",
        },
        status.HTTP_400_BAD_REQUEST: {
            "model": ErrorResponse,
            "description": "Error with course",
        },
    },
    response_model=SuccessResponse,
)
async def add_course_to_favorites(
    data: AddFavoriteCourseRequest = Body(),
    user: UserEntity = Depends(get_user),
    favorites_command_service: FavoriteCoursesCommandService = Depends(get_favorite_courses_command_service),
) -> JSONResponse:
    """Get courses.

    :param user:
    :param data:
    :param favorites_command_service:
    :return:
    """
    try:
        await favorites_command_service.add_course_to_favorites(user.id.value, data.course_id)
        return JSONResponse(
            content=SuccessResponse(message="Курс успешно добавлен в избранное").model_dump(),
            status_code=status.HTTP_201_CREATED,
        )
    except CourseAlreadyExistsInFavoritesError as ex:
        return JSONResponse(
            content=ErrorResponse(message=ex.message).model_dump(),
            status_code=status.HTTP_400_BAD_REQUEST,
        )

===== END FILE =====

===== FILE: src/api/favorite_courses/schemas.py =====
from __future__ import annotations

from typing import TYPE_CHECKING

from pydantic import BaseModel, Field

if TYPE_CHECKING:
    from src.domain.courses.entities import CourseEntity
    from src.domain.favorite_courses.entities import FavoriteCourseEntity


class AddFavoriteCourseRequest(BaseModel):

    """Schema of new favorite course."""

    course_id: str = Field("05219d1a-e1ef-4c8e-b307-89d41df8ec7b")


class FavoriteCourseDTO(BaseModel):

    """Schema of favorite course."""

    id: str = Field("05219d1a-e1ef-4c8e-b307-89d41df8ec7b")
    course_id: str = Field("05219d1a-e1ef-4c8e-b307-89d41df8ec7b")
    name: str = Field("NoSQL")
    image_url: str | None = Field("image/path-to-file.png")
    implementer: str | None = Field("ИПКН")

    @staticmethod
    def from_domain(course: CourseEntity, favorite_course: FavoriteCourseEntity) -> FavoriteCourseDTO:
        return FavoriteCourseDTO(
            id=favorite_course.id.value,
            course_id=course.id.value,
            name=course.name.value,
            image_url=course.image_url,
            implementer=course.implementer.value if course.implementer else None,
        )

===== END FILE =====

===== FILE: src/api/feedback/__init__.py =====

===== END FILE =====

===== FILE: src/api/feedback/dependencies.py =====
from fastapi import Depends
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from src.infrastructure.redis.feedback.feedback_cache_service import RedisFeedbackCacheService
from src.infrastructure.redis.session import get_redis_session
from src.infrastructure.sqlalchemy.feedback.repository import SQLAlchemyFeedbackRepository
from src.infrastructure.sqlalchemy.feedback.unit_of_work import SQLAlchemyFeedbackUnitOfWork
from src.infrastructure.sqlalchemy.session import get_async_session
from src.services.feedback.command_service import FeedbackCommandService
from src.services.feedback.query_service import FeedbackQueryService


def get_feedback_query_service(
    db_session: AsyncSession = Depends(get_async_session),
    cache_session: Redis = Depends(get_redis_session),
) -> FeedbackQueryService:
    """Get feedback service on sessions.

    :param db_session:
    :param cache_session:
    :return:
    """
    feedback_repo = SQLAlchemyFeedbackRepository(db_session)
    feedback_cache_service = RedisFeedbackCacheService(cache_session)
    return FeedbackQueryService(feedback_repo, feedback_cache_service)


def get_feedback_command_service(
    db_session: AsyncSession = Depends(get_async_session),
) -> FeedbackCommandService:
    """Get feedback service on sessions.

    :param db_session:
    :return:
    """
    unit_of_work = SQLAlchemyFeedbackUnitOfWork(db_session)
    return FeedbackCommandService(unit_of_work)

===== END FILE =====

===== FILE: src/api/feedback/router.py =====
from __future__ import annotations

from typing import TYPE_CHECKING

from fastapi import APIRouter, Body, Depends, status
from fastapi.responses import JSONResponse

from src.api.auth.dependencies import get_user, get_user_or_anonym
from src.api.base_schemas import ErrorResponse, SuccessResponse
from src.api.feedback.dependencies import get_feedback_command_service, get_feedback_query_service
from src.api.feedback.schemas import CreateFeedbackRequest, CreateFeedbackResponse, FeedbackDTO, VoteDTO
from src.domain.courses.exceptions import EmptyPropertyError, ValueDoesntExistError
from src.domain.feedback.exceptions import (
    FeedbackBelongsToAnotherUserError,
    FeedbackLikeError,
    FeedbackNotFoundError,
    OnlyOneFeedbackForCourseError,
)

if TYPE_CHECKING:
    from src.domain.auth.entities import UserEntity
    from src.services.feedback.command_service import FeedbackCommandService
    from src.services.feedback.query_service import FeedbackQueryService


router = APIRouter(prefix="/courses", tags=["courses"])


@router.get(
    "/{course_id}/feedbacks",
    status_code=status.HTTP_200_OK,
    description="Get feedback information about course",
    summary="Get feedbacks for course",
    responses={
        status.HTTP_200_OK: {
            "model": list[FeedbackDTO],
            "description": "Feedbacks for one course",
        },
    },
    response_model=list[FeedbackDTO],
)
async def get_feedbacks(
    course_id: str,
    user: UserEntity | None = Depends(get_user_or_anonym),
    query_service:  FeedbackQueryService = Depends(get_feedback_query_service),
) -> list[FeedbackDTO]:
    """Get feedbacks.

    :param user:
    :param course_id:
    :param query_service:
    :return:
    """
    feedbacks = await query_service.get_feedbacks_by_course_id(course_id)

    return [FeedbackDTO.from_domain(feedback, None if user is None else user.id.value) for feedback in feedbacks]


@router.post(
    "/{course_id}/feedbacks",
    status_code=status.HTTP_201_CREATED,
    description="Create feedback for course",
    summary="Create feedback",
    responses={
        status.HTTP_201_CREATED: {
            "model": list[FeedbackDTO],
            "description": "Feedbacks for one course",
        },
        status.HTTP_400_BAD_REQUEST: {
            "model": ErrorResponse,
            "description": "Error",
        },
        status.HTTP_422_UNPROCESSABLE_ENTITY: {
            "model": ErrorResponse,
            "description": "Error",
        },
    },
    response_model=CreateFeedbackResponse,
)
async def create_feedback(
    course_id: str,
    data: CreateFeedbackRequest = Body(),
    user: UserEntity = Depends(get_user),
    command_service:  FeedbackCommandService = Depends(get_feedback_command_service),
    query_service:  FeedbackQueryService = Depends(get_feedback_query_service),
) -> JSONResponse:
    """Create feedback.

    :param course_id:
    :param data:
    :param user:
    :param command_service:
    :param query_service:
    :return:
    """
    try:
        feedback_id = await command_service.create_feedback(course_id, user.id.value, data.text, data.rating)
        await query_service.invalidate_course(course_id)
        return JSONResponse(
            content=CreateFeedbackResponse(feedback_id=feedback_id).model_dump(),
            status_code=status.HTTP_201_CREATED,
        )
    except (EmptyPropertyError, ValueDoesntExistError) as ex:
        return JSONResponse(
            content=ErrorResponse(message=ex.message).model_dump(),
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        )
    except OnlyOneFeedbackForCourseError as ex:
        return JSONResponse(
            content=ErrorResponse(message=ex.message).model_dump(),
            status_code=status.HTTP_400_BAD_REQUEST,
        )


@router.delete(
    "/{course_id}/feedbacks/{feedback_id}",
    status_code=status.HTTP_200_OK,
    description="Delete feedback for course",
    summary="Delete feedback",
    responses={
        status.HTTP_200_OK: {
            "model": SuccessResponse,
            "description": "Feedback has been deleted",
        },
        status.HTTP_403_FORBIDDEN: {
            "model": ErrorResponse,
            "description": "Error",
        },
        status.HTTP_404_NOT_FOUND: {
            "model": ErrorResponse,
            "description": "Error",
        },
    },
    response_model=SuccessResponse,
)
async def delete_feedback(
    course_id: str,
    feedback_id: str,
    user: UserEntity = Depends(get_user),
    command_service:  FeedbackCommandService = Depends(get_feedback_command_service),
    query_service:  FeedbackQueryService = Depends(get_feedback_query_service),
) -> JSONResponse:
    """Delete feedback.

    :param course_id:
    :param feedback_id:
    :param user:
    :param command_service:
    :param query_service:
    :return:
    """
    try:
        await command_service.delete_feedback(feedback_id, user.id.value)
        await query_service.invalidate_course(course_id)
        return JSONResponse(
            content=SuccessResponse(message="Отзыв успешно удален").model_dump(),
            status_code=status.HTTP_200_OK,
        )
    except FeedbackNotFoundError as ex:
        return JSONResponse(
            content=ErrorResponse(message=ex.message).model_dump(),
            status_code=status.HTTP_404_NOT_FOUND,
        )
    except FeedbackBelongsToAnotherUserError as ex:
        return JSONResponse(
            content=ErrorResponse(message=ex.message).model_dump(),
            status_code=status.HTTP_403_FORBIDDEN,
        )


@router.delete(
    "/{course_id}/feedbacks/{feedback_id}/vote",
    status_code=status.HTTP_200_OK,
    description="Unvote feedback for course",
    summary="Unvote feedback",
    responses={
        status.HTTP_200_OK: {
            "model": list[FeedbackDTO],
            "description": "Feedback loss estimating",
        },
        status.HTTP_400_BAD_REQUEST: {
            "model": ErrorResponse,
            "description": "Error",
        },
        status.HTTP_404_NOT_FOUND: {
            "model": ErrorResponse,
            "description": "Error",
        },
        status.HTTP_422_UNPROCESSABLE_ENTITY: {
            "model": ErrorResponse,
            "description": "Error",
        },
    },
    response_model=SuccessResponse,
)
async def unvote_feedback(
    course_id: str,
    feedback_id: str,
    user: UserEntity = Depends(get_user),
    command_service:  FeedbackCommandService = Depends(get_feedback_command_service),
    query_service:  FeedbackQueryService = Depends(get_feedback_query_service),
) -> JSONResponse:
    """Unvote feedback.

    :param course_id:
    :param feedback_id:
    :param user:
    :param command_service:
    :param query_service:
    :return:
    """
    try:
        await command_service.unvote(feedback_id, user.id.value)
        await query_service.invalidate_course(course_id)
        return JSONResponse(
            content=SuccessResponse(message="Оценка с отзыва убрана").model_dump(),
            status_code=status.HTTP_200_OK,
        )
    except FeedbackNotFoundError as ex:
        return JSONResponse(
            content=ErrorResponse(message=ex.message).model_dump(),
            status_code=status.HTTP_404_NOT_FOUND,
        )
    except FeedbackLikeError as ex:
        return JSONResponse(
            content=ErrorResponse(message=ex.message).model_dump(),
            status_code=status.HTTP_400_BAD_REQUEST,
        )
    except ValueDoesntExistError as ex:
        return JSONResponse(
            content=ErrorResponse(message=ex.message).model_dump(),
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        )


@router.post(
    "/{course_id}/feedbacks/{feedback_id}/vote",
    status_code=status.HTTP_201_CREATED,
    description="Vote feedback for course",
    summary="Vote feedback",
    responses={
        status.HTTP_201_CREATED: {
            "model": SuccessResponse,
            "description": "Feedback is rated",
        },
        status.HTTP_400_BAD_REQUEST: {
            "model": ErrorResponse,
            "description": "Error",
        },
        status.HTTP_404_NOT_FOUND: {
            "model": ErrorResponse,
            "description": "Error",
        },
        status.HTTP_422_UNPROCESSABLE_ENTITY: {
            "model": ErrorResponse,
            "description": "Error",
        },
    },
    response_model=SuccessResponse,
)
async def vote_feedback(
    course_id: str,
    feedback_id: str,
    data: VoteDTO = Body(),
    user: UserEntity = Depends(get_user),
    command_service:  FeedbackCommandService = Depends(get_feedback_command_service),
    query_service:  FeedbackQueryService = Depends(get_feedback_query_service),
) -> JSONResponse:
    """Add vote for feedback.

    :param course_id:
    :param feedback_id:
    :param data:
    :param user:
    :param command_service:
    :param query_service:
    :return:
    """
    try:
        await command_service.vote(feedback_id, user.id.value, data.vote_type)
        await query_service.invalidate_course(course_id)
        return JSONResponse(
            content=SuccessResponse(message="Оценка отзыва выполнена").model_dump(),
            status_code=status.HTTP_200_OK,
        )
    except FeedbackNotFoundError as ex:
        return JSONResponse(
            content=ErrorResponse(message=ex.message).model_dump(),
            status_code=status.HTTP_404_NOT_FOUND,
        )
    except FeedbackLikeError as ex:
        return JSONResponse(
            content=ErrorResponse(message=ex.message).model_dump(),
            status_code=status.HTTP_400_BAD_REQUEST,
        )
    except ValueDoesntExistError as ex:
        return JSONResponse(
            content=ErrorResponse(message=ex.message).model_dump(),
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        )

===== END FILE =====

===== FILE: src/api/feedback/schemas.py =====
from __future__ import annotations

from typing import TYPE_CHECKING

from pydantic import BaseModel, Field

from src.domain.base_value_objects import UUID
from src.domain.feedback.value_objects import Vote

if TYPE_CHECKING:
    from src.domain.feedback.entities import FeedbackEntity

class FeedbackDTO(BaseModel):

    """Schema of feedback."""

    id: str = Field("c5a4bfb7-0349-4d07-b6d8-b21c8777602b")
    text: str = Field("Cool course!")
    rating: int = Field(5)
    is_author: bool = Field(default=False)
    liked_by_user: bool = Field(default=True)
    disliked_by_user: bool = Field(default=False)
    date: str = Field("2024-09-24")
    reputation: int = Field(3)

    @staticmethod
    def from_domain(feedback: FeedbackEntity, user_id: str | None) -> FeedbackDTO:
        return FeedbackDTO(
            id=feedback.id.value,
            text=feedback.text.value,
            rating=feedback.rating.value,
            is_author=False if user_id is None else feedback.author_id == user_id,
            liked_by_user=False if user_id is None else Vote(UUID(user_id), "like") in feedback.votes,
            disliked_by_user=False if user_id is None else Vote(UUID(user_id), "dislike") in feedback.votes,
            date=feedback.date.strftime("%Y-%m-%d"),
            reputation=feedback.reputation,
        )


class CreateFeedbackRequest(BaseModel):

    """Schema of request for creating feedback."""

    text: str = Field("Cool course!")
    rating: int = Field(5)


class CreateFeedbackResponse(BaseModel):

    """Schema of response for creating feedback."""

    feedback_id: str = Field("c5a4bfb7-0349-4d07-b6d8-b21c8777602b")


class VoteDTO(BaseModel):

    """Schema of create/delete vote."""

    vote_type: str = Field("like")

===== END FILE =====

===== FILE: src/api/playlists/__init__.py =====

===== END FILE =====

===== FILE: src/api/playlists/router.py =====
from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse

from src.api.admin.playlists.dependencies import get_playlist_service
from src.api.admin.playlists.schemas import PlaylistDTO
from src.api.base_schemas import ErrorResponse
from src.api.timetable.schemas import TimetableDTO
from src.domain.course_run.exceptions import NoActualCourseRunError
from src.services.playlists.command_service import PlaylistCommandService

router = APIRouter(prefix="/courses/{course_id}", tags=["courses"])


@router.get(
    "/playlists",
    status_code=status.HTTP_200_OK,
    description="Get actual playlists for course",
    summary="Get actual playlists",
    responses={
        status.HTTP_200_OK: {
            "model": list[TimetableDTO],
            "description": "Get actual playlists for course",
        },
        status.HTTP_404_NOT_FOUND: {
            "model": ErrorResponse,
            "description": "No actual course run",
        },
    },
    response_model=list[TimetableDTO],
)
async def get_playlists_for_course(
    course_id: str,
    command_service: PlaylistCommandService = Depends(get_playlist_service),
) -> JSONResponse:
    """Delete course run.

    :return:
    """
    try:
        playlists = await command_service.get_actual_playlists(course_id)
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=[PlaylistDTO.from_domain(p).model_dump(mode="json") for p in playlists],
        )
    except NoActualCourseRunError as ex:
        return JSONResponse(
            content=ErrorResponse(message=ex.message).model_dump(),
            status_code=status.HTTP_404_NOT_FOUND,
        )

===== END FILE =====

===== FILE: src/api/talent_profile/__init__.py =====

===== END FILE =====

===== FILE: src/api/talent_profile/dependencies.py =====
from __future__ import annotations

from typing import TYPE_CHECKING

from fastapi import Depends

from src.infrastructure.sqlalchemy.session import get_async_session
from src.infrastructure.sqlalchemy.talent_profile.unit_of_work import SQLAlchemyTalentProfileUnitOfWork
from src.services.talent_profile.command_service import TalentProfileCommandService

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


def get_talent_profile_service(
        db_session: AsyncSession = Depends(get_async_session),
) -> TalentProfileCommandService:
    """Get auth service on sessions.

    :param db_session:
    :return:
    """
    unit_of_work = SQLAlchemyTalentProfileUnitOfWork(db_session)
    return TalentProfileCommandService(unit_of_work)

===== END FILE =====

===== FILE: src/api/talent_profile/router.py =====
from fastapi import APIRouter, Body, Depends, status
from starlette.responses import JSONResponse

from src.api.auth.dependencies import get_auth_service, get_auth_token, get_user
from src.api.base_schemas import ErrorResponse, SuccessResponse
from src.api.talent_profile.dependencies import get_talent_profile_service
from src.api.talent_profile.schemas import ProfileGeneralUpdateRequest, ProfileLinksUpdateRequest, TalentProfileDTO
from src.domain.auth.entities import UserEntity
from src.domain.auth.exceptions import (
    EmptyPartOfNameError,
)
from src.domain.auth.value_objects import PartOfName
from src.domain.base_exceptions import InvalidLinkError
from src.domain.talent_profile.exceptions import (
    TalentProfileAlreadyExistsError,
    TalentProfileForOnlyTalentError,
    TalentProfileNotFoundError,
)
from src.services.auth.command_service import AuthCommandService
from src.services.talent_profile.command_service import TalentProfileCommandService

router = APIRouter(prefix="/talent", tags=["talent"])


@router.get(
    "/profile",
    status_code=status.HTTP_200_OK,
    description="Get profile of current user talent",
    summary="Getting profile",
    responses={
        status.HTTP_200_OK: {
            "model": TalentProfileDTO,
            "description": "Getting profile for current user is successful",
        },
        status.HTTP_404_NOT_FOUND: {
            "model": ErrorResponse,
            "description": "No profile",
        },
    },
    response_model=TalentProfileDTO,
)
async def get_current_user(
        user: UserEntity = Depends(get_user),
        profile_service: TalentProfileCommandService = Depends(get_talent_profile_service),
) -> JSONResponse:
    """Get current user on auth token.

    :param profile_service:
    :param user:
    :return:
    """
    try:
        profile = await profile_service.get_profile(user.id.value)
    except TalentProfileNotFoundError as ex:
        return JSONResponse(
            content=ErrorResponse(message=ex.message).model_dump(),
            status_code=status.HTTP_404_NOT_FOUND,
        )
    return JSONResponse(
        content=TalentProfileDTO.from_entity(profile, user.firstname.value, user.lastname.value).model_dump(),
        status_code=status.HTTP_200_OK,
    )


@router.put(
    "/profile/general",
    status_code=status.HTTP_200_OK,
    description="Update general part in profile",
    summary="Update profile",
    responses={
        status.HTTP_200_OK: {
            "model": SuccessResponse,
            "description": "Profile has been updated",
        },
        status.HTTP_404_NOT_FOUND: {
            "model": ErrorResponse,
            "description": "No profile",
        },
        status.HTTP_422_UNPROCESSABLE_ENTITY: {
            "model": ErrorResponse,
            "description": "invalid data",
        },
    },
    response_model=SuccessResponse,
)
async def update_profile_general(
        user: UserEntity = Depends(get_user),
        auth_token: str = Depends(get_auth_token),
        data: ProfileGeneralUpdateRequest = Body(),
        profile_service: TalentProfileCommandService = Depends(get_talent_profile_service),
        auth_service: AuthCommandService = Depends(get_auth_service),
) -> JSONResponse:
    """Update general part of profile.

    :param auth_service:
    :param auth_token:
    :param data:
    :param profile_service:
    :param user:
    :return:
    """
    try:
        await profile_service.update_profile(
            user.id.value, data.firstname, data.lastname,
            data.image_url, data.location, data.position, data.company,
        )
        if data.firstname != user.firstname or data.lastname != user.lastname:
            user.firstname = PartOfName(data.firstname)
            user.lastname = PartOfName(data.lastname)
            await auth_service.session_service.update(auth_token, user)
    except TalentProfileNotFoundError as ex:
        return JSONResponse(
            content=ErrorResponse(message=ex.message).model_dump(),
            status_code=status.HTTP_404_NOT_FOUND,
        )
    except EmptyPartOfNameError as ex:
        return JSONResponse(
            content=ErrorResponse(message=ex.message).model_dump(),
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        )
    return JSONResponse(
        content=SuccessResponse(message="Профиль успешно обновлен").model_dump(),
        status_code=status.HTTP_200_OK,
    )


@router.put(
    "/profile/links",
    status_code=status.HTTP_200_OK,
    description="Update links part in profile",
    summary="Update links",
    responses={
        status.HTTP_200_OK: {
            "model": SuccessResponse,
            "description": "Profile has been updated",
        },
        status.HTTP_404_NOT_FOUND: {
            "model": ErrorResponse,
            "description": "No profile",
        },
        status.HTTP_422_UNPROCESSABLE_ENTITY: {
            "model": ErrorResponse,
            "description": "invalid data",
        },
    },
    response_model=SuccessResponse,
)
async def update_profile_links(
        user: UserEntity = Depends(get_user),
        data: ProfileLinksUpdateRequest = Body(),
        profile_service: TalentProfileCommandService = Depends(get_talent_profile_service),
) -> JSONResponse:
    """Update general part of profile.

    :param data:
    :param profile_service:
    :param user:
    :return:
    """
    try:
        await profile_service.update_links(
            user.id.value, data.link_ru_resume, data.link_eng_resume,
            data.link_tg_personal, data.link_linkedin,
        )
    except TalentProfileNotFoundError as ex:
        return JSONResponse(
            content=ErrorResponse(message=ex.message).model_dump(),
            status_code=status.HTTP_404_NOT_FOUND,
        )
    except InvalidLinkError as ex:
        return JSONResponse(
            content=ErrorResponse(message=ex.message).model_dump(),
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        )
    return JSONResponse(
        content=SuccessResponse(message="Ссылки в профиле успешно обновлены").model_dump(),
        status_code=status.HTTP_200_OK,
    )


@router.post(
    "/profile",
    status_code=status.HTTP_201_CREATED,
    description="Create profile",
    summary="Create profile",
    responses={
        status.HTTP_200_OK: {
            "model": SuccessResponse,
            "description": "Profile has been created",
        },
        status.HTTP_400_BAD_REQUEST: {
            "model": ErrorResponse,
            "description": "Error",
        },
        status.HTTP_403_FORBIDDEN: {
            "model": ErrorResponse,
            "description": "No rights",
        },
    },
    response_model=SuccessResponse,
)
async def create_profile(
        user: UserEntity = Depends(get_user),
        profile_service: TalentProfileCommandService = Depends(get_talent_profile_service),
) -> JSONResponse:
    """Update general part of profile.

    :param profile_service:
    :param user:
    :return:
    """
    try:
        await profile_service.create_profile(user.id.value, user.role.value)
    except TalentProfileForOnlyTalentError as ex:
        return JSONResponse(
            content=ErrorResponse(message=ex.message).model_dump(),
            status_code=status.HTTP_403_FORBIDDEN,
        )
    except TalentProfileAlreadyExistsError as ex:
        return JSONResponse(
            content=ErrorResponse(message=ex.message).model_dump(),
            status_code=status.HTTP_400_BAD_REQUEST,
        )
    return JSONResponse(
        content=SuccessResponse(message="Профиль успешно создан").model_dump(),
        status_code=status.HTTP_200_OK,
    )

===== END FILE =====

===== FILE: src/api/talent_profile/schemas.py =====
from __future__ import annotations

from typing import TYPE_CHECKING

from pydantic import BaseModel, Field

if TYPE_CHECKING:
    from src.domain.talent_profile.entities import TalentProfileEntity


class ProfileGeneralUpdateRequest(BaseModel):

    """Schema of profile general information."""

    firstname: str = Field("Johny")
    lastname: str = Field("Stark")
    image_url: str | None = Field("image url")
    location: str = Field("Russia/Moscow")
    position: str = Field("ML Engineer")
    company: str = Field("Yandex")


class ProfileLinksUpdateRequest(BaseModel):

    """Schema of profile links."""

    link_ru_resume: str = Field("url")
    link_eng_resume: str = Field("url")
    link_tg_personal: str = Field("url")
    link_linkedin: str = Field("url")


class TalentProfileDTO(BaseModel):

    """Schema of talent profile."""

    user_id: str = Field("05219d1a-e1ef-4c8e-b307-89d41df8ec7b")
    firstname: str = Field("Johny")
    lastname: str = Field("Stark")
    image_url: str | None = Field("image url")
    location: str = Field("Russia/Moscow")
    position: str = Field("ML Engineer")
    company: str = Field("Yandex")
    link_ru_resume: str = Field("url")
    link_eng_resume: str = Field("url")
    link_tg_personal: str = Field("url")
    link_linkedin: str = Field("url")

    @staticmethod
    def from_entity(profile: TalentProfileEntity, firstname: str, lastname: str) -> TalentProfileDTO:
        return TalentProfileDTO(
            user_id=profile.id.value,
            firstname=firstname,
            lastname=lastname,
            image_url=profile.image_url,
            location=profile.location,
            position=profile.position,
            company=profile.company,
            link_ru_resume=profile.link_ru_resume.value,
            link_eng_resume=profile.link_eng_resume.value,
            link_tg_personal=profile.link_tg_personal.value,
            link_linkedin=profile.link_linkedin.value,
        )

===== END FILE =====

===== FILE: src/api/timetable/__init__.py =====

===== END FILE =====

===== FILE: src/api/timetable/router.py =====
from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse

from src.api.admin.course_run.dependencies import get_admin_course_run_command_service
from src.api.base_schemas import ErrorResponse
from src.api.timetable.schemas import TimetableDTO
from src.domain.course_run.exceptions import NoActualCourseRunError
from src.domain.timetable.exceptions import NoActualTimetableError
from src.services.course_run.command_service import CourseRunCommandService

router = APIRouter(prefix="/courses/{course_id}", tags=["courses"])


@router.get(
    "/timetable",
    status_code=status.HTTP_200_OK,
    description="Get actual timetable for course",
    summary="Get actual timetable",
    responses={
        status.HTTP_200_OK: {
            "model": TimetableDTO,
            "description": "Get actual timetable for course",
        },
        status.HTTP_404_NOT_FOUND: {
            "model": ErrorResponse,
            "description": "Error",
        },
    },
    response_model=TimetableDTO,
)
async def get_timetable_for_course(
    course_id: str,
    command_service: CourseRunCommandService = Depends(get_admin_course_run_command_service),
) -> JSONResponse:
    """Delete course run.

    :return:
    """
    try:
        timetable, course_run, google_calendar_groups = await command_service.get_actual_timetable_by_id(course_id)
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=TimetableDTO.from_domain(
                timetable, course_run.name.value, google_calendar_groups,
            ).model_dump(mode="json"),
        )
    except (NoActualTimetableError, NoActualCourseRunError) as ex:
        return JSONResponse(
            content=ErrorResponse(message=ex.message).model_dump(),
            status_code=status.HTTP_404_NOT_FOUND,
        )

===== END FILE =====

===== FILE: src/api/timetable/schemas.py =====
from __future__ import annotations

import datetime
from typing import TYPE_CHECKING

from pydantic import BaseModel

if TYPE_CHECKING:
    from src.domain.group_google_calendar.entities import GroupGoogleCalendarEntity
    from src.domain.timetable.entities import TimetableEntity


class LessonDTO(BaseModel):

    """Schema for lesson."""

    start_time: datetime.time
    end_time: datetime.time
    date: datetime.date


class GroupGoogleCalendarDTO(BaseModel):

    """Schema for group google calendar."""

    id: str
    name: str
    link: str

    @staticmethod
    def from_domain(group: GroupGoogleCalendarEntity) -> GroupGoogleCalendarDTO:
        return GroupGoogleCalendarDTO(
            id=group.id.value,
            name=group.name,
            link=group.link.value,
        )


class TimetableDTO(BaseModel):

    """Schema for timetable."""

    lessons: list[LessonDTO]
    course_run_name: str
    group_google_calendars: list[GroupGoogleCalendarDTO]

    @staticmethod
    def from_domain(
            timetable: TimetableEntity, course_run_name: str, google_calendar_groups: list[GroupGoogleCalendarEntity],
    ) -> TimetableDTO:
        current_lessons = timetable.lessons
        return TimetableDTO(
            lessons=[
                LessonDTO(
                    start_time=lesson.start_time.time(),
                    end_time=lesson.end_time.time(),
                    date=lesson.start_time.date(),
                ) for lesson in current_lessons],
            course_run_name=course_run_name,
            group_google_calendars=[GroupGoogleCalendarDTO.from_domain(g) for g in google_calendar_groups],
        )

===== END FILE =====

===== FILE: src/domain/__init__.py =====

===== END FILE =====

===== FILE: src/domain/base_exceptions.py =====
from dataclasses import dataclass


@dataclass(eq=False)
class DomainError(Exception):

    """Base domain error."""

    @property
    def message(self) -> str:
        return "Error in application"


class IncorrectUUIDError(DomainError):

    """Error with incorrect identifier."""

    @property
    def message(self) -> str:
        return "Identifier is not valid"


class InvalidLinkError(DomainError):

    """Error with invalid link."""

    @property
    def message(self) -> str:
        return "Link is not valid"

===== END FILE =====

===== FILE: src/domain/base_value_objects.py =====
import re
import uuid
from dataclasses import dataclass

from src.domain.base_exceptions import IncorrectUUIDError, InvalidLinkError


@dataclass(init=False, eq=True, frozen=True)
class UUID:

    """Id for entities as a value object."""

    value: str

    def __init__(self, value: str) -> None:
        """Initialize object.

        :param value:
        """
        try:
            uuid.UUID(value)
            object.__setattr__(self, "value", value)
        except ValueError as ex:
            raise IncorrectUUIDError from ex


@dataclass(init=False, eq=True, frozen=True)
class LinkValueObject:

    """Link as a value object."""

    value: str

    def __init__(self, value: str) -> None:
        """Initialize object.

        :param value:
        """
        pattern = r"^https?://[^\s]+"
        if re.match(pattern, value):
            object.__setattr__(self, "value", value)
        else:
            raise InvalidLinkError


@dataclass(init=False, eq=True, frozen=True)
class EmptyLinkValueObject:

    """Link or Empty string as a value object."""

    value: str

    def __init__(self, value: str) -> None:
        """Initialize object.

        :param value:
        """
        pattern = r"^https?://[^\s]+"
        if value == "" or re.match(pattern, value):
            object.__setattr__(self, "value", value)
        else:
            raise InvalidLinkError

===== END FILE =====

===== FILE: src/domain/auth/__init__.py =====

===== END FILE =====

===== FILE: src/domain/auth/constants.py =====
import re

EMAIL_REGULAR_EXPRESSION = r"[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,4}"
EMAIL_PATTERN = re.compile(EMAIL_REGULAR_EXPRESSION)
ADMIN_ROLE = "admin"
TALENT_ROLE = "talent"
USER_ROLES = [ADMIN_ROLE, TALENT_ROLE]
PASSWORD_MIN_LENGTH = 8
TIME_TO_LIVE_AUTH_SESSION = 60 * 60 * 24

===== END FILE =====

===== FILE: src/domain/auth/entities.py =====
from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.domain.auth.value_objects import Email, PartOfName, UserRole
    from src.domain.base_value_objects import UUID

@dataclass
class UserEntity:

    """Entity of user."""

    id: UUID
    firstname: PartOfName
    lastname: PartOfName
    role: UserRole
    email: Email
    hashed_password: str

===== END FILE =====

===== FILE: src/domain/auth/exceptions.py =====
from src.domain.auth.constants import PASSWORD_MIN_LENGTH
from src.domain.base_exceptions import DomainError


class EmailNotValidError(DomainError):

    """Email is not valid."""

    @property
    def message(self) -> str:
        return "Email is not valid"


class RoleDoesntExistError(DomainError):

    """Role does not exist."""

    @property
    def message(self) -> str:
        return "Role does not exist"


class EmptyPartOfNameError(DomainError):

    """Part of name is empty."""

    @property
    def message(self) -> str:
        return "Part of name is empty"


class UserWithEmailExistsError(DomainError):

    """User with this email already exists."""

    @property
    def message(self) -> str:
        return "User with this email already exists"


class UserNotFoundError(DomainError):

    """User is not found."""

    @property
    def message(self) -> str:
        return "User is not found"


class PasswordTooShortError(DomainError):

    """Password length must be greater than or equal to <> characters."""

    @property
    def message(self) -> str:
        return f"Password length must be greater than or equal to {PASSWORD_MIN_LENGTH} characters"


class WrongPasswordError(DomainError):

    """It is a wrong password."""

    @property
    def message(self) -> str:
        return "It is a wrong password"


class UserBySessionNotFoundError(DomainError):

    """User is not found by session."""

    @property
    def message(self) -> str:
        return "User is not found by session"

===== END FILE =====

===== FILE: src/domain/auth/user_repository.py =====
from abc import ABC, abstractmethod

from src.domain.auth.entities import UserEntity
from src.domain.auth.value_objects import Email
from src.domain.base_value_objects import UUID


class IUserRepository(ABC):

    """Interface of Repository for User."""

    @abstractmethod
    async def create(self, user: UserEntity) -> None:
        raise NotImplementedError

    @abstractmethod
    async def update(self, user: UserEntity) -> None:
        raise NotImplementedError

    @abstractmethod
    async def delete(self, user_id: UUID) -> None:
        raise NotImplementedError

    @abstractmethod
    async def get_by_id(self, user_id: UUID) -> UserEntity:
        raise NotImplementedError

    @abstractmethod
    async def get_by_email(self, email: Email) -> UserEntity:
        raise NotImplementedError

===== END FILE =====

===== FILE: src/domain/auth/value_objects.py =====
from dataclasses import dataclass

from src.domain.auth.constants import EMAIL_PATTERN, USER_ROLES
from src.domain.auth.exceptions import EmailNotValidError, EmptyPartOfNameError, RoleDoesntExistError


@dataclass(init=False, eq=True, frozen=True)
class Email:

    """Email represents an email as a value object."""

    value: str

    def __init__(self, value: str) -> None:
        """Initialize object.

        :param value:
        """
        if EMAIL_PATTERN.match(value) is None:
            raise EmailNotValidError
        object.__setattr__(self, "value", value)


@dataclass(init=False, eq=True, frozen=True)
class UserRole:

    """UserRole represents a role of user as a value object."""

    value: str

    def __init__(self, value: str) -> None:
        """Initialize object.

        :param value:
        """
        if value not in USER_ROLES:
            raise RoleDoesntExistError
        object.__setattr__(self, "value", value)


@dataclass(init=False, eq=True, frozen=True)
class PartOfName:

    """PartOfName represents a part of name as a value object."""

    value: str

    def __init__(self, value: str) -> None:
        """Initialize object.

        :param value:
        """
        if value == "":
            raise EmptyPartOfNameError
        object.__setattr__(self, "value", value)

===== END FILE =====

===== FILE: src/domain/course_run/__init__.py =====

===== END FILE =====

===== FILE: src/domain/course_run/course_run_repository.py =====
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.domain.base_value_objects import UUID
    from src.domain.course_run.entities import CourseRunEntity


class ICourseRunRepository(ABC):

    """Interface of Repository for Course run."""

    @abstractmethod
    async def create(self, course_run: CourseRunEntity) -> None:
        raise NotImplementedError

    @abstractmethod
    async def delete(self, course_run_id: UUID) -> None:
        raise NotImplementedError

    @abstractmethod
    async def get_by_id(self, course_run_id: UUID) -> CourseRunEntity:
        raise NotImplementedError

    @abstractmethod
    async def get_all_by_course_id(self, course_id: UUID) -> list[CourseRunEntity]:
        raise NotImplementedError

===== END FILE =====

===== FILE: src/domain/course_run/entities.py =====
from __future__ import annotations

import datetime
from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.domain.base_value_objects import UUID
    from src.domain.courses.value_objects import CourseRun


@dataclass
class CourseRunEntity:

    """Entity of timetable."""

    id: UUID
    course_id: UUID
    name: CourseRun

    def is_actual_by_date(self, current_date: datetime.date) -> bool:
        month, year = current_date.month, current_date.year
        run_season, run_year = self.name.season, self.name.year
        if run_season == "Осень":
            # С предзаписи и до конца осеннего семестра
            return year == run_year and month in (8, 9, 10, 11, 12) or year == run_year + 1 and month == 1
        # С предзаписи и до конца весеннего семестра
        return year == run_year and month in (1, 2, 3, 4, 5, 6, 7)

===== END FILE =====

===== FILE: src/domain/course_run/exceptions.py =====
from src.domain.base_exceptions import DomainError


class CourseRunNotFoundError(DomainError):

    """Course run is not found."""

    @property
    def message(self) -> str:
        return "Запуск курса не найден"


class CourseRunAlreadyExistsError(DomainError):

    """Course run is already exists."""

    @property
    def message(self) -> str:
        return "Запуск курса уже существует"


class NoActualCourseRunError(DomainError):

    """Course run doesnt exist."""

    @property
    def message(self) -> str:
        return "Для курса еще не создан актуальный запуск"

===== END FILE =====

===== FILE: src/domain/courses/__init__.py =====

===== END FILE =====

===== FILE: src/domain/courses/course_repository.py =====
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.domain.base_value_objects import UUID
    from src.domain.courses.entities import CourseEntity
    from src.domain.courses.value_objects import CourseName

class ICourseRepository(ABC):

    """Interface of Repository for Course."""

    @abstractmethod
    async def create(self, course: CourseEntity) -> None:
        raise NotImplementedError

    @abstractmethod
    async def update(self, course: CourseEntity) -> None:
        raise NotImplementedError

    @abstractmethod
    async def update_draft_status(self, course: CourseEntity) -> None:
        raise NotImplementedError

    @abstractmethod
    async def delete(self, course_id: UUID) -> None:
        raise NotImplementedError

    @abstractmethod
    async def get_by_id(self, course_id: UUID) -> CourseEntity:
        raise NotImplementedError

    @abstractmethod
    async def get_by_name(self, course_name: CourseName) -> CourseEntity:
        raise NotImplementedError

    @abstractmethod
    async def get_all(self) -> list[CourseEntity]:
        raise NotImplementedError

===== END FILE =====

===== FILE: src/domain/courses/entities.py =====
from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from src.domain.courses.exceptions import CoursePublishError

if TYPE_CHECKING:
    from src.domain.base_value_objects import UUID
    from src.domain.courses.value_objects import (
        Author,
        CourseName,
        CourseRun,
        Format,
        Implementer,
        Period,
        Resource,
        Role,
        Terms,
    )


@dataclass
class CourseEntity:

    """Entity of course."""

    id: UUID
    name: CourseName
    image_url: str | None = field(default=None)
    limits: int | None = field(default=None)
    is_draft: bool = field(default=True)

    prerequisites: str | None = field(default=None)
    description: str | None = field(default=None)
    topics: str | None = field(default=None)
    assessment: str | None = field(default=None)
    resources: list[Resource] = field(default_factory=list)
    extra: str | None = field(default=None)

    author: Author | None = field(default=None)
    implementer: Implementer | None = field(default=None)
    format: Format | None = field(default=None)
    terms: Terms | None = field(default=None)
    roles: list[Role] = field(default_factory=list)
    periods: list[Period] = field(default_factory=list)
    last_runs: list[CourseRun] = field(default_factory=list)

    def publish(self) -> None:
        if not self.is_draft:
            raise CoursePublishError(error_message="Course has already published")
        if self.image_url is None:
            raise CoursePublishError(error_message="No image for course")
        if self.author is None:
            raise CoursePublishError(error_message="No author for course")
        if self.implementer is None:
            raise CoursePublishError(error_message="No implementer for course")
        if self.format is None:
            raise CoursePublishError(error_message="No format for course")
        if self.terms is None:
            raise CoursePublishError(error_message="No terms for course")
        if self.roles is None:
            raise CoursePublishError(error_message="No roles for course")
        if self.periods is None:
            raise CoursePublishError(error_message="No time of implementing course")
        self.is_draft = False

    def hide(self) -> None:
        if self.is_draft:
            raise CoursePublishError(error_message="Course has already hided")
        self.is_draft = True

===== END FILE =====

===== FILE: src/domain/courses/exceptions.py =====
from dataclasses import dataclass

from src.domain.base_exceptions import DomainError


@dataclass
class ValueDoesntExistError(DomainError):

    """Value of property does not exist."""

    property_name: str

    @property
    def message(self) -> str:
        return f"Такой {self.property_name} не существует"


@dataclass
class EmptyPropertyError(DomainError):

    """Property is empty."""

    property_name: str

    @property
    def message(self) -> str:
        return f"{self.property_name.capitalize()} is empty"


class IncorrectCourseRunNameError(DomainError):

    """Course run has incorrect name."""

    @property
    def message(self) -> str:
        return "Course run has incorrect name"


@dataclass
class CoursePublishError(DomainError):

    """Course run has incorrect name."""

    error_message: str

    @property
    def message(self) -> str:
        return self.error_message


class CourseNotFoundError(DomainError):

    """Course is not found."""

    @property
    def message(self) -> str:
        return "Course is not found"


class CourseAlreadyExistsError(DomainError):

    """Course with this name already exists."""

    @property
    def message(self) -> str:
        return "Course with this name already exists"

===== END FILE =====

===== FILE: src/domain/courses/value_objects.py =====
from dataclasses import dataclass

from src.domain.courses.constants import (
    COURSE_RUN_FROM_YEAR,
    COURSE_RUN_SEASONS,
    COURSE_RUN_TO_YEAR,
    FORMATS,
    IMPLEMENTERS,
    PERIODS,
    ROLES,
)
from src.domain.courses.exceptions import EmptyPropertyError, IncorrectCourseRunNameError, ValueDoesntExistError


@dataclass(init=False, eq=True, frozen=True)
class CourseName:

    """Name of course as a value object."""

    value: str

    def __init__(self, value: str) -> None:
        """Initialize object.

        :param value:
        """
        if value == "":
            raise EmptyPropertyError(property_name="course")
        object.__setattr__(self, "value", value)


@dataclass(init=False, eq=True, frozen=True)
class Author:

    """Author information as a value object."""

    value: str

    def __init__(self, value: str) -> None:
        """Initialize object.

        :param value:
        """
        if value == "":
            raise EmptyPropertyError(property_name="author")
        object.__setattr__(self, "value", value)


@dataclass(init=False, eq=True, frozen=True)
class Implementer:

    """Implementer represents an implementer as a value object."""

    value: str

    def __init__(self, value: str) -> None:
        """Initialize object.

        :param value:
        """
        if value not in IMPLEMENTERS:
            raise ValueDoesntExistError(property_name="implementer")
        object.__setattr__(self, "value", value)


@dataclass(init=False, eq=True, frozen=True)
class Format:

    """Format represents an format as a value object."""

    value: str

    def __init__(self, value: str) -> None:
        """Initialize object.

        :param value:
        """
        if value not in FORMATS:
            raise ValueDoesntExistError(property_name="format")
        object.__setattr__(self, "value", value)


@dataclass(init=False, eq=True, frozen=True)
class Terms:

    """Term numbers as a value object."""

    value: str

    def __init__(self, value: str) -> None:
        """Initialize object.

        :param value:
        """
        digits = sorted([digit.strip() for digit in value.split(",")])
        for digit in digits:
            if not digit.isdigit():
                raise ValueDoesntExistError(property_name="terms")
        object.__setattr__(self, "value", ", ".join(digits))


@dataclass(init=False, eq=True, frozen=True)
class Role:

    """Role name as a value object."""

    value: str

    def __init__(self, value: str) -> None:
        """Initialize object.

        :param value:
        """
        if value not in ROLES:
            raise ValueDoesntExistError(property_name="role")
        object.__setattr__(self, "value", value)


@dataclass(init=False, eq=True, frozen=True)
class Period:

    """Period name as a value object: september, november and other."""

    value: str

    def __init__(self, value: str) -> None:
        """Initialize object.

        :param value:
        """
        if value not in PERIODS:
            raise ValueDoesntExistError(property_name="period")
        object.__setattr__(self, "value", value)


@dataclass(init=False, eq=True, frozen=True)
class CourseRun:

    """Run of course as a value object: Autumn 2023."""

    value: str

    def __init__(self, value: str) -> None:
        """Initialize object.

        :param value:
        """
        try:
            season, year_string = value.split()
            if season not in COURSE_RUN_SEASONS:
                raise IncorrectCourseRunNameError
            year = int(year_string)
            if year < COURSE_RUN_FROM_YEAR or year > COURSE_RUN_TO_YEAR:
                raise IncorrectCourseRunNameError
        except ValueError as ex:
            raise IncorrectCourseRunNameError from ex
        object.__setattr__(self, "value", value)

    @property
    def year(self) -> int:
        return int(self.value.split(" ")[1])

    @property
    def season(self) -> str:
        return self.value.split(" ")[0]


@dataclass(init=True, eq=True, frozen=True)
class Resource:

    """Resource of course as a value object."""

    title: str
    link: str

===== END FILE =====

===== FILE: src/domain/favorite_courses/__init__.py =====

===== END FILE =====

===== FILE: src/domain/favorite_courses/entities.py =====
from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.domain.base_value_objects import UUID


@dataclass
class FavoriteCourseEntity:

    """Entity of talent profile."""

    id: UUID
    user_id: UUID
    course_id: UUID

===== END FILE =====

===== FILE: src/domain/favorite_courses/exceptions.py =====
from src.domain.base_exceptions import DomainError


class CourseAlreadyExistsInFavoritesError(DomainError):

    """Course is already exists in favorites."""

    @property
    def message(self) -> str:
        return "Курс уже добавлен в избранное"


class CourseDoesntExistInFavoritesError(DomainError):

    """Course doesnt exist in favorites."""

    @property
    def message(self) -> str:
        return "Курс не добавлен в избранное"

===== END FILE =====

===== FILE: src/domain/favorite_courses/favorite_courses_repository.py =====
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.domain.base_value_objects import UUID
    from src.domain.favorite_courses.entities import FavoriteCourseEntity


class IFavoriteCourseRepository(ABC):

    """Interface of Repository for favorite course."""

    @abstractmethod
    async def add_one(self, favorite_course: FavoriteCourseEntity) -> None:
        raise NotImplementedError

    @abstractmethod
    async def delete_one(self, favorite_course_id: UUID) -> None:
        raise NotImplementedError

    @abstractmethod
    async def get_all_by_user_id(self, user_id: UUID) -> list[FavoriteCourseEntity]:
        raise NotImplementedError

    @abstractmethod
    async def get_one_by_course_id_and_user_id(self, course_id: UUID, user_id: UUID) -> FavoriteCourseEntity:
        raise NotImplementedError

===== END FILE =====

===== FILE: src/domain/feedback/__init__.py =====

===== END FILE =====

===== FILE: src/domain/feedback/contants.py =====
VOTE_TYPES = ["like", "dislike"]
MAX_RATING_VALUE = 5
MIN_RATING_VALUE = 1

===== END FILE =====

===== FILE: src/domain/feedback/entities.py =====
from __future__ import annotations

import datetime
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from src.domain.feedback.exceptions import FeedbackLikeError
from src.domain.feedback.value_objects import FeedbackText, Rating, Vote

if TYPE_CHECKING:
    from src.domain.base_value_objects import UUID

@dataclass
class FeedbackEntity:

    """Entity of feedback."""

    id: UUID
    course_id: UUID
    author_id: UUID
    text: FeedbackText
    rating: Rating
    votes: set[Vote] = field(default_factory=list)
    date: datetime.date = field(default_factory=datetime.date.today)

    def unvote(self, user_id: UUID) -> None:
        vote = Vote(user_id, "like")
        alternative_vote = Vote(user_id, "dislike")
        self.votes.discard(vote)
        self.votes.discard(alternative_vote)

    def vote(self, user_id: UUID, vote_type: str) -> None:
        alternative_vote_type = "dislike" if vote_type == "like" else "like"
        alternative_vote = Vote(user_id, alternative_vote_type)
        vote = Vote(user_id, vote_type)
        if self.author_id == user_id:
            raise FeedbackLikeError(error_message="Невозможно оценивать свой отзыв")
        if vote in self.votes:
            raise FeedbackLikeError(error_message="Отзыв уже оценен")
        if alternative_vote in self.votes:
            self.votes.remove(alternative_vote)
            self.votes.add(vote)
        else:
            self.votes.add(vote)

    @property
    def reputation(self) -> int:
        reputation = 0
        for vote in self.votes:
            signed_vote = 1 if vote.vote_type == "like" else -1
            reputation += signed_vote
        return reputation

===== END FILE =====

===== FILE: src/domain/feedback/exceptions.py =====
from dataclasses import dataclass

from src.domain.base_exceptions import DomainError


@dataclass
class FeedbackLikeError(DomainError):

    """Error with estimating feedback of course."""

    error_message: str

    @property
    def message(self) -> str:
        return self.error_message


class FeedbackNotFoundError(DomainError):

    """Feedback is not found."""

    @property
    def message(self) -> str:
        return "Отзыв не найден"


class FeedbackBelongsToAnotherUserError(DomainError):

    """Feedback belongs to another author."""

    @property
    def message(self) -> str:
        return "Для удаления отзыва требуется быть автором"


class OnlyOneFeedbackForCourseError(DomainError):

    """Feedback is only one for course by user."""

    @property
    def message(self) -> str:
        return "Нельзя создать больше одного отзыва на курс"

===== END FILE =====

===== FILE: src/domain/feedback/feedback_repository.py =====
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.domain.base_value_objects import UUID
    from src.domain.feedback.entities import FeedbackEntity


class IFeedbackRepository(ABC):

    """Interface of Repository for Feedback."""

    @abstractmethod
    async def create(self, feedback: FeedbackEntity) -> None:
        raise NotImplementedError

    @abstractmethod
    async def delete(self, feedback_id: UUID) -> None:
        raise NotImplementedError

    @abstractmethod
    async def update_votes(self, feedback: FeedbackEntity) -> None:
        raise NotImplementedError

    @abstractmethod
    async def get_one_by_id(self, feedback_id: UUID) -> FeedbackEntity:
        raise NotImplementedError

    @abstractmethod
    async def get_all_by_course_id(self, course_id: UUID) -> list[FeedbackEntity]:
        raise NotImplementedError

===== END FILE =====

===== FILE: src/domain/feedback/value_objects.py =====
from dataclasses import dataclass

from src.domain.base_value_objects import UUID
from src.domain.courses.exceptions import EmptyPropertyError, ValueDoesntExistError
from src.domain.feedback.contants import MAX_RATING_VALUE, MIN_RATING_VALUE, VOTE_TYPES


@dataclass(init=False, eq=True, frozen=True)
class Vote:

    """Name of course as a value object."""

    user_id: UUID
    vote_type: str

    def __init__(self, user_id: UUID, vote_type: str) -> None:
        """Initialize object."""
        if vote_type not in VOTE_TYPES:
            raise ValueDoesntExistError(property_name="vote type")
        object.__setattr__(self, "user_id", user_id)
        object.__setattr__(self, "vote_type", vote_type)


@dataclass(init=False, eq=True, frozen=True)
class FeedbackText:

    """Content of feedback as a value object."""

    value: str

    def __init__(self, value: str) -> None:
        """Initialize object.

        :param value:
        """
        if value == "":
            raise EmptyPropertyError(property_name="text")
        object.__setattr__(self, "value", value)


@dataclass(init=False, eq=True, frozen=True)
class Rating:

    """Rating of course in feedback as a value object."""

    value: int

    def __init__(self, value: int) -> None:
        """Initialize object.

        :param value:
        """
        if value < MIN_RATING_VALUE or value > MAX_RATING_VALUE:
            raise ValueDoesntExistError(property_name="rating")
        object.__setattr__(self, "value", value)

===== END FILE =====

===== FILE: src/domain/group_google_calendar/__init__.py =====

===== END FILE =====

===== FILE: src/domain/group_google_calendar/entities.py =====
from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.domain.base_value_objects import UUID, LinkValueObject


@dataclass
class GroupGoogleCalendarEntity:

    """Entity of group timetable for day."""

    id: UUID
    course_run_id: UUID
    name: str  # name of group, optional
    link: LinkValueObject

===== END FILE =====

===== FILE: src/domain/group_google_calendar/exceptions.py =====
from src.domain.base_exceptions import DomainError


class GroupGoogleCalendarNotFoundError(DomainError):

    """Group google calendar is not found."""

    @property
    def message(self) -> str:
        return "Расписание в Google-календаре не существует"

===== END FILE =====

===== FILE: src/domain/group_google_calendar/ggc_repository.py =====
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.domain.base_value_objects import UUID
    from src.domain.group_google_calendar.entities import GroupGoogleCalendarEntity


class IGroupGoogleCalendarRepository(ABC):

    """Interface of Repository for Feedback."""

    @abstractmethod
    async def create(self, group_google_calendar: GroupGoogleCalendarEntity) -> None:
        raise NotImplementedError

    @abstractmethod
    async def delete(self, group_google_calendar_id: UUID) -> None:
        raise NotImplementedError

    @abstractmethod
    async def get_all_by_course_run_id(self, course_run_id: UUID) -> list[GroupGoogleCalendarEntity]:
        raise NotImplementedError

===== END FILE =====

===== FILE: src/domain/playlists/__init__.py =====

===== END FILE =====

===== FILE: src/domain/playlists/constants.py =====
VIDEO_RESOURCE_TYPES = ["vk", "youtube"]

===== END FILE =====

===== FILE: src/domain/playlists/entities.py =====
from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.domain.base_value_objects import UUID, LinkValueObject
    from src.domain.playlists.value_objects import VideoResourceType


@dataclass
class PlaylistEntity:

    """Entity of group timetable for day."""

    id: UUID
    course_run_id: UUID
    name: str  # name of resource, optional
    type: VideoResourceType
    link: LinkValueObject

===== END FILE =====

===== FILE: src/domain/playlists/exceptions.py =====
from src.domain.base_exceptions import DomainError


class PlaylistNotFoundError(DomainError):

    """Video playlist is not found."""

    @property
    def message(self) -> str:
        return "Плейлист не существует"

===== END FILE =====

===== FILE: src/domain/playlists/playlist_repository.py =====
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.domain.base_value_objects import UUID
    from src.domain.playlists.entities import PlaylistEntity


class IPlaylistRepository(ABC):

    """Interface of Repository for Video playlist."""

    @abstractmethod
    async def create(self, playlist: PlaylistEntity) -> None:
        raise NotImplementedError

    @abstractmethod
    async def update(self, playlist: PlaylistEntity) -> None:
        raise NotImplementedError

    @abstractmethod
    async def delete(self, playlist_id: UUID) -> None:
        raise NotImplementedError

    @abstractmethod
    async def get_all_by_course_run_id(self, course_run_id: UUID) -> list[PlaylistEntity]:
        raise NotImplementedError

===== END FILE =====

===== FILE: src/domain/playlists/value_objects.py =====
from dataclasses import dataclass

from src.domain.courses.exceptions import ValueDoesntExistError
from src.domain.playlists.constants import VIDEO_RESOURCE_TYPES


@dataclass(init=False, eq=True, frozen=True)
class VideoResourceType:

    """Video resource type as a value object: vk, youtube."""

    value: str

    def __init__(self, value: str) -> None:
        """Initialize object.

        :param value:
        """
        if value not in VIDEO_RESOURCE_TYPES:
            raise ValueDoesntExistError(property_name="тип видеоресурса")
        object.__setattr__(self, "value", value)

===== END FILE =====

===== FILE: src/domain/talent_profile/__init__.py =====

===== END FILE =====

===== FILE: src/domain/talent_profile/entities.py =====
from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from src.domain.base_value_objects import EmptyLinkValueObject

if TYPE_CHECKING:
    from src.domain.base_value_objects import UUID


@dataclass
class TalentProfileEntity:

    """Entity of talent profile."""

    id: UUID
    image_url: str | None = field(default=None)
    location: str = field(default="")
    position: str = field(default="")
    company: str = field(default="")
    link_ru_resume: EmptyLinkValueObject = field(default=EmptyLinkValueObject(""))
    link_eng_resume: EmptyLinkValueObject = field(default=EmptyLinkValueObject(""))
    link_tg_personal: EmptyLinkValueObject = field(default=EmptyLinkValueObject(""))
    link_linkedin: EmptyLinkValueObject = field(default=EmptyLinkValueObject(""))

    def update_profile(self, image_url: str | None, location: str, position: str, company: str) -> None:
        self.image_url = image_url
        self.location = location
        self.position = position
        self.company = company

    def update_links(
            self, link_ru_resume: EmptyLinkValueObject, link_eng_resume: EmptyLinkValueObject,
            link_tg_personal: EmptyLinkValueObject, link_linkedin: EmptyLinkValueObject,
    ) -> None:
        self.link_ru_resume = link_ru_resume
        self.link_eng_resume = link_eng_resume
        self.link_tg_personal = link_tg_personal
        self.link_linkedin = link_linkedin

===== END FILE =====

===== FILE: src/domain/talent_profile/exceptions.py =====
from src.domain.base_exceptions import DomainError


class TalentProfileNotFoundError(DomainError):

    """Talent profile is not found."""

    @property
    def message(self) -> str:
        return "Профиль таланта не существует"


class TalentProfileAlreadyExistsError(DomainError):

    """Talent profile already exists."""

    @property
    def message(self) -> str:
        return "Профиль таланта уже существует"


class TalentProfileForOnlyTalentError(DomainError):

    """Talent profile is only for talent."""

    @property
    def message(self) -> str:
        return "Профиль таланта можно создать только для таланта"

===== END FILE =====

===== FILE: src/domain/talent_profile/profile_repository.py =====
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.domain.base_value_objects import UUID
    from src.domain.talent_profile.entities import TalentProfileEntity


class ITalentProfileRepository(ABC):

    """Interface of Repository for Course."""

    @abstractmethod
    async def create(self, profile: TalentProfileEntity) -> None:
        raise NotImplementedError

    @abstractmethod
    async def update(self, profile: TalentProfileEntity) -> None:
        raise NotImplementedError

    @abstractmethod
    async def delete(self, user_id: UUID) -> None:
        raise NotImplementedError

    @abstractmethod
    async def get_by_user_id(self, user_id: UUID) -> TalentProfileEntity:
        raise NotImplementedError

===== END FILE =====

===== FILE: src/domain/timetable/__init__.py =====

===== END FILE =====

===== FILE: src/domain/timetable/entities.py =====
from __future__ import annotations

import datetime
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from src.domain.timetable.constants import WEEKDAYS
from src.domain.timetable.exceptions import TimetableError
from src.domain.timetable.value_objects import LessonTimeDuration, TimetableWarning, Weekday

if TYPE_CHECKING:
    from src.domain.base_value_objects import UUID


@dataclass
class DayRuleEntity:

    """Entity of timetable rule for day."""

    id: UUID
    timetable_id: UUID
    start_time: datetime.time
    end_time: datetime.time
    date: datetime.date

    @property
    def lessons(self) -> list[LessonTimeDuration]:
        year, month, day = self.date.year, self.date.month, self.date.day
        return [LessonTimeDuration(
            datetime.datetime(year, month, day, self.start_time.hour, self.start_time.minute, self.start_time.second),
            datetime.datetime(year, month, day, self.end_time.hour, self.end_time.minute, self.end_time.second),
        )]


@dataclass
class WeekRuleEntity:

    """Entity of timetable rule for week."""

    id: UUID
    timetable_id: UUID
    start_time: datetime.time
    end_time: datetime.time
    start_period_date: datetime.date
    end_period_date: datetime.date
    weekdays: list[Weekday]

    @property
    def lessons(self) -> list[LessonTimeDuration]:
        current_lessons: list[LessonTimeDuration] = []
        current_date = self.start_period_date
        while current_date <= self.end_period_date:
            weekday = Weekday(WEEKDAYS[current_date.weekday()])
            if weekday not in self.weekdays:
                current_date = current_date + datetime.timedelta(days=1)
                continue
            year, month, day = current_date.year, current_date.month, current_date.day
            lesson = LessonTimeDuration(
                datetime.datetime(year, month, day, self.start_time.hour, self.start_time.minute,
                                  self.start_time.second),
                datetime.datetime(year, month, day, self.end_time.hour, self.end_time.minute, self.end_time.second),
            )
            current_lessons.append(lesson)
            current_date = current_date + datetime.timedelta(days=1)
        current_lessons.sort(key=lambda lesson: lesson.start_time)
        return current_lessons


@dataclass
class TimetableEntity:

    """Entity of timetable."""

    id: UUID  # соответствует course_run_id
    course_run_id: UUID
    rules: list[DayRuleEntity | WeekRuleEntity] = field(default_factory=list)

    @property
    def lessons(self) -> list[LessonTimeDuration]:
        current_lessons: list[LessonTimeDuration] = []
        for rule in self.rules:
            current_lessons.extend(rule.lessons)
        current_lessons.sort(key=lambda lesson: lesson.start_time)
        return current_lessons

    @property
    def warnings(self) -> set[TimetableWarning]:
        current_lessons = self.lessons
        current_warnings = set()
        for i in range(len(current_lessons)):
            for j in range(i + 1, len(current_lessons)):
                if current_lessons[i].start_time.date() != current_lessons[j].start_time.date():
                    continue
                if current_lessons[i].start_time <= current_lessons[j].end_time and current_lessons[j].start_time <= \
                        current_lessons[i].end_time:
                    warning = TimetableWarning(current_lessons[i].start_time.date(), "Пересечение занятий в этот день")
                    current_warnings.add(warning)
        return current_warnings

    def check_lesson_intersection(self, other: TimetableEntity) -> None:
        lesson_intersection_error = TimetableError("Курсы имеют пересечения по времени проведения занятий")
        other_lessons = set(other.lessons)
        current_lessons = set(self.lessons)
        if current_lessons.intersection(other_lessons):
            raise lesson_intersection_error
        for current_lesson in current_lessons:
            for other_lesson in other_lessons:
                if current_lesson.start_time.date() != other_lesson.start_time.date():
                    continue
                if (current_lesson.start_time < other_lesson.end_time
                        and other_lesson.start_time < current_lesson.end_time):
                    raise lesson_intersection_error

===== END FILE =====

===== FILE: src/domain/timetable/exceptions.py =====
from dataclasses import dataclass

from src.domain.base_exceptions import DomainError


@dataclass
class TimetableError(DomainError):

    """Error with timetable."""

    error_message: str

    @property
    def message(self) -> str:
        return self.error_message


class RuleNotFoundError(DomainError):

    """Rule is not found."""

    @property
    def message(self) -> str:
        return "Правило формирования расписания не найдено"


class IncorrectRuleTypeError(DomainError):

    """Rule type is not valid."""

    @property
    def message(self) -> str:
        return "Некорректный или несоответствующий тип правила"


@dataclass
class NoActualTimetableError(DomainError):

    """Timetable is not available for course."""

    error_message: str

    @property
    def message(self) -> str:
        return self.error_message

===== END FILE =====

===== FILE: src/domain/timetable/timetable_repository.py =====
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.domain.base_value_objects import UUID
    from src.domain.timetable.entities import DayRuleEntity, TimetableEntity, WeekRuleEntity


class ITimetableRepository(ABC):

    """Interface of Repository for Timetable."""

    @abstractmethod
    async def get_by_id(self, course_run_id: UUID) -> TimetableEntity:
        raise NotImplementedError

    @abstractmethod
    async def create_rule(self, rule: DayRuleEntity | WeekRuleEntity) -> None:
        raise NotImplementedError

    @abstractmethod
    async def update_rule(self, rule: DayRuleEntity | WeekRuleEntity) -> None:
        raise NotImplementedError

    @abstractmethod
    async def delete_rule(self, rule_id: UUID) -> None:
        raise NotImplementedError

===== END FILE =====

===== FILE: src/domain/timetable/value_objects.py =====
import datetime
from dataclasses import dataclass

from src.domain.courses.exceptions import ValueDoesntExistError
from src.domain.timetable.constants import WEEKDAYS


@dataclass(init=True, eq=True, frozen=True)
class LessonTimeDuration:

    """Lesson time duration as value object."""

    start_time: datetime.datetime
    end_time: datetime.datetime


@dataclass(init=False, eq=True, frozen=True)
class Weekday:

    """Weekday as a value object: пн, вт and other."""

    value: str

    def __init__(self, value: str) -> None:
        """Initialize object.

        :param value:
        """
        if value not in WEEKDAYS:
            raise ValueDoesntExistError(property_name="weekday")
        object.__setattr__(self, "value", value)


@dataclass(init=True, eq=True, frozen=True)
class TimetableWarning:

    """Timetable warning as a value object."""

    day: datetime.date
    message: str

===== END FILE =====

===== FILE: src/infrastructure/__init__.py =====

===== END FILE =====

===== FILE: src/infrastructure/fastapi/__init__.py =====

===== END FILE =====

===== FILE: src/infrastructure/fastapi/docs.py =====
from fastapi import FastAPI
from fastapi.openapi.docs import (
    get_redoc_html,
    get_swagger_ui_html,
    get_swagger_ui_oauth2_redirect_html,
)
from fastapi.responses import HTMLResponse

SWAGGER_JS_URL = "https://unpkg.com/swagger-ui-dist@5/swagger-ui-bundle.js"
SWAGGER_CSS_URL = "https://unpkg.com/swagger-ui-dist@5/swagger-ui.css"
REDOC_JS_URL = "https://unpkg.com/redoc@next/bundles/redoc.standalone.js"


def add_custom_docs_endpoints(app: FastAPI) -> None:
    """Add rewritten docs endpoints with another url of static files (JS, CSS for Swagger and Redoc).

    :param app: FastAPI-application
    :return: None
    """
    @app.get("/docs", include_in_schema=False)
    async def custom_swagger_ui_html() -> HTMLResponse:
        return get_swagger_ui_html(
            openapi_url=app.openapi_url,
            title=app.title + " - Swagger UI",
            oauth2_redirect_url=app.swagger_ui_oauth2_redirect_url,
            swagger_js_url=SWAGGER_JS_URL,
            swagger_css_url=SWAGGER_CSS_URL,
        )

    @app.get(app.swagger_ui_oauth2_redirect_url, include_in_schema=False)
    async def swagger_ui_redirect() -> HTMLResponse:
        return get_swagger_ui_oauth2_redirect_html()

    @app.get("/redoc", include_in_schema=False)
    async def redoc_html() -> HTMLResponse:
        return get_redoc_html(
            openapi_url=app.openapi_url,
            title=app.title + " - ReDoc",
            redoc_js_url=REDOC_JS_URL,
        )

===== END FILE =====

===== FILE: src/infrastructure/redis/__init__.py =====

===== END FILE =====

===== FILE: src/infrastructure/redis/session.py =====
from redis import asyncio as aioredis
from redis.asyncio import Redis

from src.config import app_config

pool = aioredis.ConnectionPool.from_url(app_config.cache_url, max_connections=10)


async def get_redis_session() -> Redis:
    """Get Redis sesion.

    :return:
    """
    async with aioredis.Redis(connection_pool=pool) as session:
        yield session

===== END FILE =====

===== FILE: src/infrastructure/redis/auth/__init__.py =====

===== END FILE =====

===== FILE: src/infrastructure/redis/auth/session_service.py =====
import json
from json.decoder import JSONDecodeError

from redis.asyncio import Redis

from src.domain.auth.constants import TIME_TO_LIVE_AUTH_SESSION
from src.domain.auth.entities import UserEntity
from src.domain.auth.exceptions import UserBySessionNotFoundError
from src.domain.auth.value_objects import Email, PartOfName, UserRole
from src.domain.base_value_objects import UUID
from src.services.auth.session_service import SessionService


class RedisSessionService(SessionService):

    """Redis implementation of session service."""

    def __init__(self, session: Redis) -> None:
        self.session = session

    @staticmethod
    def from_domain_to_json_string(user: UserEntity) -> str:
        user_dict = {
            "id": user.id.value,
            "firstname": user.firstname.value,
            "lastname": user.lastname.value,
            "role": user.role.value,
            "email": user.email.value,
            "hashed_password": user.hashed_password,
        }
        return json.dumps(user_dict)

    async def get(self, auth_token: str) -> UserEntity:
        try:
            user_data_string = await self.session.get(auth_token)
            user_dict = json.loads(user_data_string)
            return UserEntity(
                id=UUID(user_dict["id"]),
                firstname=PartOfName(user_dict["firstname"]),
                lastname=PartOfName(user_dict["lastname"]),
                role=UserRole(user_dict["role"]),
                email=Email(user_dict["email"]),
                hashed_password=user_dict["hashed_password"],
            )
        except (TypeError, JSONDecodeError) as ex:  # no such key in Redis
            raise UserBySessionNotFoundError from ex

    async def update(self, auth_token: str, user: UserEntity) -> None:
        user_data_string = self.from_domain_to_json_string(user)
        remaining_ttl = await self.session.ttl(auth_token)
        await self.session.set(auth_token, user_data_string, keepttl=remaining_ttl)

    async def set(self, auth_token: str, user: UserEntity) -> None:
        user_data_string = self.from_domain_to_json_string(user)
        await self.session.setex(auth_token, TIME_TO_LIVE_AUTH_SESSION, user_data_string)

    async def delete(self, auth_token: str) -> None:
        await self.session.delete(auth_token)

===== END FILE =====

===== FILE: src/infrastructure/redis/courses/__init__.py =====

===== END FILE =====

===== FILE: src/infrastructure/redis/courses/constants.py =====
TIME_TO_LIVE_ALL_COURSES = 60 * 60
TIME_TO_LIVE_ONE_COURSE = 24 * 60 * 60

===== END FILE =====

===== FILE: src/infrastructure/redis/courses/course_cache_service.py =====
from __future__ import annotations

import json
from json.decoder import JSONDecodeError
from typing import TYPE_CHECKING, Literal

from src.domain.base_value_objects import UUID
from src.domain.courses.entities import CourseEntity
from src.domain.courses.value_objects import (
    Author,
    CourseName,
    CourseRun,
    Format,
    Implementer,
    Period,
    Resource,
    Role,
    Terms,
)
from src.infrastructure.redis.courses.constants import TIME_TO_LIVE_ALL_COURSES, TIME_TO_LIVE_ONE_COURSE
from src.services.courses.course_cache_service import CourseCacheService

if TYPE_CHECKING:
    from redis.asyncio import Redis


class RedisCourseCacheService(CourseCacheService):

    """Redis implementation class for cache of course as service."""

    def __init__(self, session: Redis, prefix: Literal["admin", "talent", "test"]) -> None:
        self.session = session
        self.prefix = prefix

    def __get_course_key(self, course_id: UUID) -> str:
        return self.prefix + "-course-" + course_id.value

    def __get_courses_key(self) -> str:
        return self.prefix + "-courses"

    @staticmethod
    def __from_domain_to_dict(course: CourseEntity) -> dict:
        return {
            "id": course.id.value,
            "name": course.name.value,
            "image_url": course.image_url,
            "limits": course.limits,
            "is_draft": course.is_draft,
            "prerequisites": course.prerequisites,
            "description": course.description,
            "topics": course.topics,
            "assessment": course.assessment,
            "resources": [{"title": res.title, "link": res.link} for res in course.resources],
            "extra": course.extra,
            "author": course.author.value if course.author else None,
            "implementer": course.implementer.value if course.implementer else None,
            "format": course.format.value if course.format else None,
            "terms": course.terms.value if course.terms else None,
            "roles": [item.value for item in course.roles],
            "periods": [item.value for item in course.periods],
            "last_runs": [item.value for item in course.last_runs],
        }

    @staticmethod
    def __from_dict_to_domain(course_: dict) -> CourseEntity:
        return CourseEntity(
            id=UUID(course_["id"]),
            name=CourseName(course_["name"]),
            image_url=course_["image_url"],
            limits=course_["limits"],
            is_draft=course_["is_draft"],
            prerequisites=course_["prerequisites"],
            description=course_["description"],
            topics=course_["topics"],
            assessment=course_["assessment"],
            resources=[Resource(title=res["title"], link=res["link"]) for res in course_["resources"]],
            extra=course_["extra"],
            author=Author(course_["author"]) if course_["author"] else None,
            implementer=Implementer(course_["implementer"]) if course_["implementer"] else None,
            format=Format(course_["format"]) if course_["format"] else None,
            terms=Terms(course_["terms"]) if course_["terms"] else None,
            roles=[Role(role) for role in course_["roles"]],
            periods=[Period(period) for period in course_["periods"]],
            last_runs=[CourseRun(run) for run in course_["last_runs"]],
        )

    async def get_one(self, course_id: UUID) -> CourseEntity | None:
        try:
            course_data_string = await self.session.get(self.__get_course_key(course_id))
            course_dict = json.loads(course_data_string)
            return self.__from_dict_to_domain(course_dict)
        except (TypeError, JSONDecodeError):  # no such key in Redis
            return None

    async def delete_one(self, course_id: UUID) -> None:
        await self.session.delete(self.__get_course_key(course_id))

    async def set_one(self, course: CourseEntity) -> None:
        course_dict = self.__from_domain_to_dict(course)
        course_data_string = json.dumps(course_dict)
        await self.session.setex(self.__get_course_key(course.id), TIME_TO_LIVE_ONE_COURSE, course_data_string)

    async def get_many(self) -> list[CourseEntity] | None:
        try:
            courses_data_string = await self.session.get(self.__get_courses_key())
            courses_dict = json.loads(courses_data_string)
            return [self.__from_dict_to_domain(course_dict) for course_dict in courses_dict]
        except (TypeError, JSONDecodeError):  # no such key in Redis
            return None

    async def delete_many(self) -> None:
        await self.session.delete(self.__get_courses_key())

    async def set_many(self, courses: list[CourseEntity]) -> None:
        courses_dict = [self.__from_domain_to_dict(course) for course in courses]
        courses_data_string = json.dumps(courses_dict)
        await self.session.setex(self.__get_courses_key(), TIME_TO_LIVE_ALL_COURSES, courses_data_string)

===== END FILE =====

===== FILE: src/infrastructure/redis/feedback/__init__.py =====

===== END FILE =====

===== FILE: src/infrastructure/redis/feedback/constants.py =====
TIME_TO_LIVE_FEEDBACKS = 60 * 60

===== END FILE =====

===== FILE: src/infrastructure/redis/feedback/feedback_cache_service.py =====
from __future__ import annotations

import datetime
import json
from json.decoder import JSONDecodeError
from typing import TYPE_CHECKING

from src.domain.base_value_objects import UUID
from src.domain.feedback.entities import FeedbackEntity
from src.domain.feedback.value_objects import FeedbackText, Rating, Vote
from src.infrastructure.redis.feedback.constants import TIME_TO_LIVE_FEEDBACKS
from src.services.feedback.feedback_cache_service import FeedbackCacheService

if TYPE_CHECKING:
    from redis.asyncio import Redis


class RedisFeedbackCacheService(FeedbackCacheService):

    """Redis implementation class for cache of course as service."""

    def __init__(self, session: Redis) -> None:
        self.session = session

    @staticmethod
    def feedback_key(course_id: UUID) -> str:
        return "course_" + course_id.value + "_feedbacks"

    @staticmethod
    def __from_domain_to_dict(feedback: FeedbackEntity) -> dict:
        return {
            "id": feedback.id.value,
            "course_id": feedback.course_id.value,
            "author_id": feedback.author_id.value,
            "text": feedback.text.value,
            "rating": feedback.rating.value,
            "votes": [{"user_id": vote.user_id.value, "vote_type": vote.vote_type} for vote in feedback.votes],
            "date": feedback.date.strftime("%Y-%m-%d"),
        }

    @staticmethod
    def __from_dict_to_domain(feedback_: dict) -> FeedbackEntity:
        return FeedbackEntity(
            id=UUID(feedback_["id"]),
            course_id=UUID(feedback_["course_id"]),
            author_id=UUID(feedback_["author_id"]),
            text=FeedbackText(feedback_["text"]),
            rating=Rating(feedback_["rating"]),
            votes={Vote(UUID(vote["user_id"]), vote["vote_type"]) for vote in feedback_["votes"]},
            date=datetime.date.fromisoformat(feedback_["date"]),
        )

    async def get_many_by_course_id(self, course_id: UUID) -> list[FeedbackEntity] | None:
        try:
            feedbacks_key = self.feedback_key(course_id)
            feedbacks_data_string = await self.session.get(feedbacks_key)
            feedbacks_data = json.loads(feedbacks_data_string)
            return [self.__from_dict_to_domain(feedback) for feedback in feedbacks_data]
        except (TypeError, JSONDecodeError):  # no such key in Redis
            return None

    async def delete_many(self, course_id: UUID) -> None:
        feedbacks_key = self.feedback_key(course_id)
        await self.session.delete(feedbacks_key)

    async def set_many(self, course_id: UUID, feedbacks: list[FeedbackEntity]) -> None:
        feedbacks_key = self.feedback_key(course_id)
        feedbacks_data = [self.__from_domain_to_dict(feedback) for feedback in feedbacks]
        course_data_string = json.dumps(feedbacks_data)
        await self.session.setex(feedbacks_key, TIME_TO_LIVE_FEEDBACKS, course_data_string)

===== END FILE =====

===== FILE: src/infrastructure/security/__init__.py =====

===== END FILE =====

===== FILE: src/infrastructure/security/password_service.py =====
import hashlib
import os

from src.domain.auth.constants import PASSWORD_MIN_LENGTH
from src.domain.auth.exceptions import PasswordTooShortError, WrongPasswordError


class PasswordService:

    """Service for work with passwords."""

    @staticmethod
    def validate_password(password: str) -> None:
        if len(password) < PASSWORD_MIN_LENGTH:
            raise PasswordTooShortError

    @staticmethod
    def create_hashed_password(password: str) -> str:
        salt = os.urandom(32)
        encoded_password = password.encode("UTF-8")
        key = hashlib.pbkdf2_hmac("sha256", encoded_password, salt, 100000)
        return key.hex() + "." + salt.hex()

    @staticmethod
    def verify_password(try_password: str, hashed_password: str) -> None:
        encoded_try_password = try_password.encode("UTF-8")
        key, salt = hashed_password.split(".")
        try_key = hashlib.pbkdf2_hmac("sha256", encoded_try_password, bytes.fromhex(salt), 100000)
        real_key = bytes.fromhex(key)
        if try_key != real_key:
            raise WrongPasswordError

===== END FILE =====

===== FILE: src/infrastructure/sqlalchemy/__init__.py =====

===== END FILE =====

===== FILE: src/infrastructure/sqlalchemy/base_unit_of_work.py =====
from sqlalchemy.ext.asyncio import AsyncSession

from src.services.base_unit_of_work import ServiceUnitOfWork


class SQLAlchemyUnitOfWork(ServiceUnitOfWork):

    """SQLA implementation for unit of work."""

    def __init__(self, sqla_session: AsyncSession) -> None:
        self.session = sqla_session

    async def begin(self) -> None:
        await self.session.begin()

    async def commit(self) -> None:
        await self.session.commit()

    async def rollback(self) -> None:
        await self.session.rollback()

===== END FILE =====

===== FILE: src/infrastructure/sqlalchemy/session.py =====
from sqlalchemy import MetaData
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import declarative_base

from src.config import app_config

async_engine = create_async_engine(url=app_config.db_url, echo=app_config.is_debug)
async_session_factory = async_sessionmaker(
    bind=async_engine, autocommit=False, autoflush=False,
)
meta = MetaData(
    naming_convention={
        "ix": "ix_%(column_0_label)s",
        "uq": "uq_%(table_name)s_%(column_0_name)s",
        "ck": "ck_%(table_name)s_%(constraint_name)s",
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
        "pk": "pk_%(table_name)s",
    },
)


async def get_async_session() -> AsyncSession:
    """Get async session for db queries.

    :return: AsyncSession
    """
    async with async_session_factory() as session:
        yield session


Base = declarative_base(metadata=meta)

===== END FILE =====

===== FILE: src/infrastructure/sqlalchemy/course_run/__init__.py =====

===== END FILE =====

===== FILE: src/infrastructure/sqlalchemy/course_run/models.py =====
from __future__ import annotations

import datetime
import uuid

from sqlalchemy import UniqueConstraint, text
from sqlalchemy.orm import Mapped, mapped_column

from src.domain.base_value_objects import UUID
from src.domain.course_run.entities import CourseRunEntity
from src.domain.courses.value_objects import CourseRun as CourseRunName
from src.infrastructure.sqlalchemy.session import Base


class CourseRun(Base):

    """SQLAlchemy model of Course."""

    __tablename__ = "course_runs_"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True)
    course_id: Mapped[uuid.UUID] = mapped_column(nullable=False)
    name: Mapped[str] = mapped_column(nullable=False)
    is_archive: Mapped[bool] = mapped_column(nullable=False, default=False)

    created_at: Mapped[datetime.datetime] = mapped_column(
        server_default=text("TIMEZONE('utc', now())"),
    )
    updated_at: Mapped[datetime.datetime] = mapped_column(
        server_default=text("TIMEZONE('utc', now())"),
        onupdate=datetime.datetime.utcnow,
    )

    __table_args__ = (UniqueConstraint("course_id", "name", name="uix_course_id_name"),)

    @staticmethod
    def from_domain(course_run: CourseRunEntity) -> CourseRun:
        return CourseRun(
            id=course_run.id.value,
            course_id=course_run.course_id.value,
            name=course_run.name.value,
        )

    def to_domain(self) -> CourseRunEntity:
        return CourseRunEntity(
            id=UUID(str(self.id)),
            course_id=UUID(str(self.course_id)),
            name=CourseRunName(self.name),
        )

===== END FILE =====

===== FILE: src/infrastructure/sqlalchemy/course_run/repository.py =====
from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import select
from sqlalchemy.exc import NoResultFound

from src.domain.course_run.course_run_repository import ICourseRunRepository
from src.domain.course_run.exceptions import CourseRunNotFoundError
from src.infrastructure.sqlalchemy.course_run.models import CourseRun

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

    from src.domain.base_value_objects import UUID
    from src.domain.course_run.entities import CourseRunEntity


class SQLAlchemyCourseRunRepository(ICourseRunRepository):

    """SQLAlchemy's implementation of Repository for Course."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, course_run: CourseRunEntity) -> None:
        course_run_ = CourseRun.from_domain(course_run)
        self.session.add(course_run_)

    async def delete(self, course_run_id: UUID) -> None:
        course_run_ = await self.__get_by_id(course_run_id)
        course_run_.is_archive = True
        # to avoid unique error after creating new course run
        course_run_.name = f"{course_run_.name} - {course_run_.id}"

    async def get_by_id(self, course_run_id: UUID) -> CourseRunEntity:
        course_run = await self.__get_by_id(course_run_id)
        return course_run.to_domain()

    async def __get_by_id(self, course_run_id: UUID) -> CourseRun:
        query = (
            select(CourseRun)
            .filter_by(id=course_run_id.value, is_archive=False)
        )
        try:
            result = await self.session.execute(query)
            return result.unique().scalars().one()
        except NoResultFound as ex:
            raise CourseRunNotFoundError from ex

    async def get_all_by_course_id(self, course_id: UUID) -> list[CourseRunEntity]:
        query = (
            select(CourseRun)
            .filter_by(course_id=course_id.value, is_archive=False)
            .order_by(CourseRun.created_at.desc())
        )
        result = await self.session.execute(query)
        course_runs = result.unique().scalars().all()
        return [course_run.to_domain() for course_run in course_runs]

===== END FILE =====

===== FILE: src/infrastructure/sqlalchemy/course_run/unit_of_work.py =====
from sqlalchemy.ext.asyncio import AsyncSession

from src.infrastructure.sqlalchemy.base_unit_of_work import SQLAlchemyUnitOfWork
from src.infrastructure.sqlalchemy.course_run.repository import SQLAlchemyCourseRunRepository
from src.infrastructure.sqlalchemy.group_google_calendar.repository import SQLAlchemyGroupGoogleCalendarRepository
from src.infrastructure.sqlalchemy.timetable.repository import SQLAlchemyTimetableRepository
from src.services.course_run.unit_of_work import CourseRunUnitOfWork


class SQLAlchemyCourseRunUnitOfWork(SQLAlchemyUnitOfWork, CourseRunUnitOfWork):

    """SQLA implementation for unit of work."""

    def __init__(self, sqla_session: AsyncSession) -> None:
        super().__init__(sqla_session)
        self.course_run_repo = SQLAlchemyCourseRunRepository(sqla_session)
        self.timetable_repo = SQLAlchemyTimetableRepository(sqla_session)
        self.ggc_repo = SQLAlchemyGroupGoogleCalendarRepository(sqla_session)

===== END FILE =====

===== FILE: src/infrastructure/sqlalchemy/courses/__init__.py =====

===== END FILE =====

===== FILE: src/infrastructure/sqlalchemy/courses/models.py =====
from __future__ import annotations

import datetime
import json
import uuid

from sqlalchemy import ForeignKey, Text, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.domain.base_value_objects import UUID
from src.domain.courses.entities import CourseEntity
from src.domain.courses.value_objects import (
    Author,
    CourseName,
    CourseRun,
    Format,
    Implementer,
    Period,
    Resource,
    Role,
    Terms,
)
from src.infrastructure.sqlalchemy.session import Base


class Course(Base):

    """SQLAlchemy model of Course."""

    __tablename__ = "courses"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(nullable=False, unique=True)
    image_url: Mapped[str] = mapped_column(nullable=True)
    limits: Mapped[int] = mapped_column(nullable=True)
    is_draft: Mapped[bool] = mapped_column(nullable=False, default=True)
    is_archive: Mapped[bool] = mapped_column(nullable=False, default=False)

    prerequisites: Mapped[str] = mapped_column(Text, nullable=True)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    topics: Mapped[str] = mapped_column(Text, nullable=True)
    assessment: Mapped[str] = mapped_column(Text, nullable=True)
    resources: Mapped[str] = mapped_column(Text, nullable=True)
    extra: Mapped[str] = mapped_column(Text, nullable=True)

    author: Mapped[str] = mapped_column(nullable=True)
    implementer: Mapped[str] = mapped_column(nullable=True)
    format: Mapped[str] = mapped_column(nullable=True)
    terms: Mapped[str] = mapped_column(nullable=True)

    roles: Mapped[list[RoleForCourse]] = relationship(back_populates="course")
    periods: Mapped[list[PeriodForCourse]] = relationship(back_populates="course")
    runs: Mapped[list[RunForCourse]] = relationship(back_populates="course")

    created_at: Mapped[datetime.datetime] = mapped_column(
        server_default=text("TIMEZONE('utc', now())"),
    )
    updated_at: Mapped[datetime.datetime] = mapped_column(
        server_default=text("TIMEZONE('utc', now())"),
        onupdate=datetime.datetime.utcnow,
    )

    @staticmethod
    def from_domain(course: CourseEntity) -> Course:
        resources_json_string = json.dumps(course.resources)
        return Course(
            id=course.id.value,
            name=course.name.value,
            image_url=course.image_url,
            limits=course.limits,
            prerequisites=course.prerequisites,
            description=course.description,
            topics=course.topics,
            assessment=course.assessment,
            resources=resources_json_string,
            extra=course.extra,
            author=course.author.value if course.author else None,
            implementer=course.implementer.value if course.implementer else None,
            format=course.format.value if course.format else None,
            terms=course.terms.value if course.terms else None,
            roles=[RoleForCourse(course_id=course.id, role_name=role.value) for role in course.roles],
            periods=[PeriodForCourse(course_id=course.id, period_name=period.value) for period in course.periods],
            runs=[RunForCourse(course_id=course.id, run_name=run.value) for run in course.last_runs],
        )

    def to_domain(self) -> CourseEntity:
        course_ = self
        try:
            resources = json.loads(course_.resources)
        except (json.decoder.JSONDecodeError, TypeError):
            resources = []
        return CourseEntity(
            id=UUID(str(course_.id)),
            name=CourseName(course_.name),
            image_url=course_.image_url,
            limits=course_.limits,
            is_draft=course_.is_draft,
            prerequisites=course_.prerequisites,
            description=course_.description,
            topics=course_.topics,
            assessment=course_.assessment,
            resources=[Resource(title=res["title"], link=res["link"]) for res in resources],
            extra=course_.extra,
            author=Author(str(course_.author)) if course_.author else None,
            implementer=Implementer(str(course_.implementer)) if course_.implementer else None,
            format=Format(str(course_.format)) if course_.format else None,
            terms=Terms(str(course_.terms)) if course_.terms else None,
            roles=[Role(role.role_name) for role in course_.roles],
            periods=[Period(period.period_name) for period in course_.periods],
            last_runs=[CourseRun(run.run_name) for run in course_.runs],
        )


class RoleForCourse(Base):

    """SQLAlchemy model of Role for course."""

    __tablename__ = "course_roles"

    course_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("courses.id"), primary_key=True)
    role_name: Mapped[str] = mapped_column(primary_key=True)
    course: Mapped[Course] = relationship(back_populates="roles")


class PeriodForCourse(Base):

    """SQLAlchemy model of Period for course."""

    __tablename__ = "course_periods"

    course_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("courses.id"), primary_key=True)
    period_name: Mapped[str] = mapped_column(primary_key=True)
    course: Mapped[Course] = relationship(back_populates="periods")


class RunForCourse(Base):

    """SQLAlchemy model of Period for course."""

    __tablename__ = "course_runs"

    course_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("courses.id"), primary_key=True)
    run_name: Mapped[str] = mapped_column(primary_key=True)
    course: Mapped[Course] = relationship(back_populates="runs")

===== END FILE =====

===== FILE: src/infrastructure/sqlalchemy/courses/repository.py =====
from __future__ import annotations

import json
from typing import TYPE_CHECKING

from sqlalchemy import select
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import joinedload

from src.domain.courses.course_repository import ICourseRepository
from src.domain.courses.exceptions import CourseNotFoundError
from src.infrastructure.sqlalchemy.courses.models import Course, PeriodForCourse, RoleForCourse, RunForCourse

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

    from src.domain.base_value_objects import UUID
    from src.domain.courses.entities import CourseEntity
    from src.domain.courses.value_objects import CourseName


class SQLAlchemyCourseRepository(ICourseRepository):

    """SQLAlchemy's implementation of Repository for Course."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, course: CourseEntity) -> None:
        course_ = Course.from_domain(course)
        self.session.add(course_)

    async def update(self, course: CourseEntity) -> None:
        course_ = await self.__get_by_id(course.id)
        course_.name = course.name.value
        course_.image_url = course.image_url
        course_.limits = course.limits
        course_.prerequisites = course.prerequisites
        course_.description = course.description
        course_.topics = course.topics
        course_.assessment = course.assessment
        course_.resources = json.dumps([{"link": res.link, "title": res.title} for res in course.resources])
        course_.extra = course.extra
        course_.author = course.author.value if course.author else None
        course_.implementer = course.implementer.value if course.implementer else None
        course_.format = course.format.value if course.format else None
        course_.terms = course.terms.value if course.terms else None

        for role in course_.roles:
            await self.session.delete(role)

        for period in course_.periods:
            await self.session.delete(period)

        for run in course_.runs:
            await self.session.delete(run)

        course_.roles = [RoleForCourse(course_id=course.id, role_name=role.value) for role in course.roles]
        course_.periods = [PeriodForCourse(course_id=course.id, period_name=period.value) for period in course.periods]
        course_.runs = [RunForCourse(course_id=course.id, run_name=run.value) for run in course.last_runs]

    async def update_draft_status(self, course: CourseEntity) -> None:
        course_ = await self.__get_by_id(course.id)
        course_.is_draft = course.is_draft

    async def delete(self, course_id: UUID) -> None:
        course_ = await self.__get_by_id(course_id)
        course_.is_archive = True  # many related data
        course_.name = f"{course_.name} - {course_.id}"  # to avoid unique name after creating new course

    async def get_by_id(self, course_id: UUID) -> CourseEntity:
        try:
            course_ = await self.__get_by_id(course_id)
            return course_.to_domain()
        except NoResultFound as ex:
            raise CourseNotFoundError from ex

    async def get_by_name(self, course_name: CourseName) -> CourseEntity:
        query = (
            select(Course)
            .options(joinedload(Course.roles))
            .options(joinedload(Course.periods))
            .options(joinedload(Course.runs))
            .filter_by(name=course_name.value, is_archive=False)
        )
        try:
            result = await self.session.execute(query)
            course_ = result.unique().scalars().one()
            return course_.to_domain()
        except NoResultFound as ex:
            raise CourseNotFoundError from ex

    async def __get_by_id(self, course_id: UUID) -> Course:
        query = (
            select(Course)
            .options(joinedload(Course.roles))
            .options(joinedload(Course.periods))
            .options(joinedload(Course.runs))
            .filter_by(id=course_id.value, is_archive=False)
        )
        try:
            result = await self.session.execute(query)
            return result.unique().scalars().one()
        except NoResultFound as ex:
            raise CourseNotFoundError from ex

    async def get_all(self) -> list[CourseEntity]:
        query = (
            select(Course)
            .options(joinedload(Course.roles))
            .options(joinedload(Course.periods))
            .options(joinedload(Course.runs))
            .filter_by(is_archive=False)
        )
        result = await self.session.execute(query)
        courses = result.unique().scalars().all()
        return [course.to_domain() for course in courses]

===== END FILE =====

===== FILE: src/infrastructure/sqlalchemy/courses/unit_of_work.py =====
from sqlalchemy.ext.asyncio import AsyncSession

from src.infrastructure.sqlalchemy.courses.repository import SQLAlchemyCourseRepository
from src.infrastructure.sqlalchemy.users.repository import SQLAlchemyUserRepository
from src.services.courses.unit_of_work import CoursesUnitOfWork


class SQLAlchemyCoursesUnitOfWork(CoursesUnitOfWork):

    """SQLA implementation for unit of work."""

    def __init__(self, sqla_session: AsyncSession) -> None:
        self.session = sqla_session
        self.user_repo = SQLAlchemyUserRepository(sqla_session)
        self.course_repo = SQLAlchemyCourseRepository(sqla_session)

    async def begin(self) -> None:
        await self.session.begin()

    async def commit(self) -> None:
        await self.session.commit()

    async def rollback(self) -> None:
        await self.session.rollback()

===== END FILE =====

===== FILE: src/infrastructure/sqlalchemy/favorite_courses/__init__.py =====

===== END FILE =====

===== FILE: src/infrastructure/sqlalchemy/favorite_courses/models.py =====
from __future__ import annotations

import datetime
import uuid

from sqlalchemy import UniqueConstraint, text
from sqlalchemy.orm import Mapped, mapped_column

from src.domain.base_value_objects import UUID
from src.domain.favorite_courses.entities import FavoriteCourseEntity
from src.infrastructure.sqlalchemy.session import Base


class FavoriteCourse(Base):

    """SQLAlchemy model of Course."""

    __tablename__ = "favorite_courses"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True)
    user_id: Mapped[uuid.UUID] = mapped_column(nullable=False)
    course_id: Mapped[uuid.UUID] = mapped_column(nullable=False)

    created_at: Mapped[datetime.datetime] = mapped_column(
        server_default=text("TIMEZONE('utc', now())"),
    )
    updated_at: Mapped[datetime.datetime] = mapped_column(
        server_default=text("TIMEZONE('utc', now())"),
        onupdate=datetime.datetime.utcnow,
    )

    __table_args__ = (UniqueConstraint("user_id", "course_id", name="uix_course_id_user_id"),)

    @staticmethod
    def from_domain(favorite_course: FavoriteCourseEntity) -> FavoriteCourse:
        return FavoriteCourse(
            id=favorite_course.id.value,
            user_id=favorite_course.user_id.value,
            course_id=favorite_course.course_id.value,
        )

    def to_domain(self) -> FavoriteCourseEntity:
        return FavoriteCourseEntity(
            id=UUID(str(self.id)),
            user_id=UUID(str(self.user_id)),
            course_id=UUID(str(self.course_id)),
        )

===== END FILE =====

===== FILE: src/infrastructure/sqlalchemy/favorite_courses/repository.py =====
from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import select
from sqlalchemy.exc import NoResultFound

from src.domain.favorite_courses.exceptions import CourseDoesntExistInFavoritesError
from src.domain.favorite_courses.favorite_courses_repository import IFavoriteCourseRepository
from src.infrastructure.sqlalchemy.favorite_courses.models import FavoriteCourse

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

    from src.domain.base_value_objects import UUID
    from src.domain.favorite_courses.entities import FavoriteCourseEntity


class SQLAlchemyFavoriteCourseRepository(IFavoriteCourseRepository):

    """SQLAlchemy's implementation of Repository for Course."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def add_one(self, favorite_course: FavoriteCourseEntity) -> None:
        course_ = FavoriteCourse.from_domain(favorite_course)
        self.session.add(course_)

    async def delete_one(self, favorite_course_id: UUID) -> None:
        favorite_course_ = await self.__get_by_id(favorite_course_id)
        await self.session.delete(favorite_course_)

    async def __get_by_id(self, favorite_course_id: UUID) -> FavoriteCourse:
        query = (
            select(FavoriteCourse)
            .filter_by(id=favorite_course_id.value)
        )
        try:
            result = await self.session.execute(query)
            return result.scalars().one()
        except NoResultFound as ex:
            raise CourseDoesntExistInFavoritesError from ex

    async def get_all_by_user_id(self, user_id: UUID) -> list[FavoriteCourseEntity]:
        query = (
            select(FavoriteCourse)
            .filter_by(user_id=user_id.value)
        )
        result = await self.session.execute(query)
        favorite_courses = result.unique().scalars().all()
        return [course.to_domain() for course in favorite_courses]

    async def get_one_by_course_id_and_user_id(self, course_id: UUID, user_id: UUID) -> FavoriteCourseEntity:
        query = (
            select(FavoriteCourse)
            .filter_by(course_id=course_id.value, user_id=user_id.value)
        )
        try:
            result = await self.session.execute(query)
            favorite_course = result.scalars().one()
            return favorite_course.to_domain()
        except NoResultFound as ex:
            raise CourseDoesntExistInFavoritesError from ex

===== END FILE =====

===== FILE: src/infrastructure/sqlalchemy/favorite_courses/unit_of_work.py =====
from sqlalchemy.ext.asyncio import AsyncSession

from src.infrastructure.sqlalchemy.base_unit_of_work import SQLAlchemyUnitOfWork
from src.infrastructure.sqlalchemy.courses.repository import SQLAlchemyCourseRepository
from src.infrastructure.sqlalchemy.favorite_courses.repository import SQLAlchemyFavoriteCourseRepository
from src.services.favorite_courses.unit_of_work import FavoriteCoursesUnitOfWork


class SQLAlchemyFavoritesUnitOfWork(SQLAlchemyUnitOfWork, FavoriteCoursesUnitOfWork):

    """SQLA implementation for unit of work."""

    def __init__(self, sqla_session: AsyncSession) -> None:
        super().__init__(sqla_session)
        self.course_repo = SQLAlchemyCourseRepository(sqla_session)
        self.favorites_repo = SQLAlchemyFavoriteCourseRepository(sqla_session)

===== END FILE =====

===== FILE: src/infrastructure/sqlalchemy/feedback/__init__.py =====

===== END FILE =====

===== FILE: src/infrastructure/sqlalchemy/feedback/models.py =====
from __future__ import annotations

import datetime
import uuid

from sqlalchemy import Date, ForeignKey, Integer, Text, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.domain.base_value_objects import UUID
from src.domain.feedback.entities import FeedbackEntity
from src.domain.feedback.value_objects import FeedbackText, Rating, Vote
from src.infrastructure.sqlalchemy.session import Base


class Feedback(Base):

    """SQLAlchemy model of Feedback."""

    __tablename__ = "feedbacks"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True)
    course_id: Mapped[uuid.UUID] = mapped_column(nullable=False)
    author_id: Mapped[uuid.UUID] = mapped_column(nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    rating: Mapped[int] = mapped_column(Integer, server_default="5", nullable=False)
    votes: Mapped[list[VoteForFeedback]] = relationship(back_populates="feedback")
    date: Mapped[datetime.date] = mapped_column(Date, nullable=False)

    is_archive: Mapped[bool] = mapped_column(nullable=False, default=False)

    created_at: Mapped[datetime.datetime] = mapped_column(
        server_default=text("TIMEZONE('utc', now())"),
    )
    updated_at: Mapped[datetime.datetime] = mapped_column(
        server_default=text("TIMEZONE('utc', now())"),
        onupdate=datetime.datetime.utcnow,
    )

    @staticmethod
    def from_domain(feedback: FeedbackEntity) -> Feedback:
        return Feedback(
            id=uuid.UUID(feedback.id.value),
            course_id=uuid.UUID(feedback.course_id.value),
            author_id=uuid.UUID(feedback.author_id.value),
            content=feedback.text.value,
            rating=feedback.rating.value,
            date=feedback.date,
            votes=[
                VoteForFeedback(
                    feedback_id=uuid.UUID(feedback.id.value),
                    user_id=uuid.UUID(vote.user_id.value),
                    vote_type=vote.vote_type,
                )
                for vote in feedback.votes
            ],
        )

    def to_domain(self) -> FeedbackEntity:
        return FeedbackEntity(
            id=UUID(str(self.id)),
            course_id=UUID(str(self.course_id)),
            author_id=UUID(str(self.author_id)),
            text=FeedbackText(self.content),
            rating=Rating(self.rating),
            votes={Vote(user_id=UUID(str(vote.user_id)), vote_type=vote.vote_type) for vote in self.votes},
            date=self.date,
        )


class VoteForFeedback(Base):

    """SQLAlchemy model of Vote for feedback."""

    __tablename__ = "feedback_votes"

    feedback_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("feedbacks.id"), primary_key=True)
    user_id: Mapped[uuid.UUID] = mapped_column(primary_key=True)
    vote_type: Mapped[str] = mapped_column(nullable=False)
    feedback: Mapped[Feedback] = relationship(back_populates="votes")
    created_at: Mapped[datetime.datetime] = mapped_column(
        server_default=text("TIMEZONE('utc', now())"),
    )

    @staticmethod
    def from_domain(vote: Vote, feedback_id: UUID) -> VoteForFeedback:
        return VoteForFeedback(
           feedback_id=uuid.UUID(feedback_id.value),
           user_id=uuid.UUID(vote.user_id.value),
           vote_type=vote.vote_type,
        )

===== END FILE =====

===== FILE: src/infrastructure/sqlalchemy/feedback/repository.py =====
from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import select
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import joinedload

from src.domain.feedback.exceptions import FeedbackNotFoundError, OnlyOneFeedbackForCourseError
from src.domain.feedback.feedback_repository import IFeedbackRepository
from src.infrastructure.sqlalchemy.feedback.models import Feedback, VoteForFeedback

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

    from src.domain.base_value_objects import UUID
    from src.domain.feedback.entities import FeedbackEntity


class SQLAlchemyFeedbackRepository(IFeedbackRepository):

    """SQLAlchemy's implementation of Repository for Course."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, feedback: FeedbackEntity) -> None:
        await self.__check_one_by_user_id_and_course_id(feedback.author_id, feedback.course_id)
        feedback_ = Feedback.from_domain(feedback)
        self.session.add(feedback_)

    async def update_votes(self, feedback: FeedbackEntity) -> None:
        feedback_ = await self.__get_by_id(feedback.id)
        for vote in feedback_.votes:
            await self.session.delete(vote)
        for vote in feedback.votes:
            self.session.add(VoteForFeedback.from_domain(vote, feedback.id))

    async def delete(self, feedback_id: UUID) -> None:
        feedback_ = await self.__get_by_id(feedback_id)
        feedback_.is_archive = True  # to avoid cascade deleting

    async def get_one_by_id(self, feedback_id: UUID) -> FeedbackEntity:
        feedback_ = await self.__get_by_id(feedback_id)
        return feedback_.to_domain()

    async def __get_by_id(self, feedback_id: UUID) -> Feedback:
        query = (
            select(Feedback)
            .options(joinedload(Feedback.votes))
            .filter_by(id=feedback_id.value, is_archive=False)
        )
        try:
            result = await self.session.execute(query)
            return result.unique().scalars().one()
        except NoResultFound as ex:
            raise FeedbackNotFoundError from ex

    async def __check_one_by_user_id_and_course_id(self, author_id: UUID, course_id: UUID) -> None:
        query = (
            select(Feedback.id)
            .filter_by(author_id=author_id.value, course_id=course_id.value, is_archive=False)
        )
        try:
            result = await self.session.execute(query)
            feedback_id = result.unique().scalar()
            if feedback_id:
                raise OnlyOneFeedbackForCourseError
        except NoResultFound:
            pass

    async def get_all_by_course_id(self, course_id: UUID) -> list[FeedbackEntity]:
        query = (
            select(Feedback)
            .options(joinedload(Feedback.votes))
            .filter_by(course_id=course_id.value, is_archive=False)
            .order_by(Feedback.date.desc())
        )
        result = await self.session.execute(query)
        feedbacks = result.unique().scalars().all()
        return [feedback.to_domain() for feedback in feedbacks]

===== END FILE =====

===== FILE: src/infrastructure/sqlalchemy/feedback/unit_of_work.py =====
from sqlalchemy.ext.asyncio import AsyncSession

from src.infrastructure.sqlalchemy.feedback.repository import SQLAlchemyFeedbackRepository
from src.services.feedback.unit_of_work import FeedbackUnitOfWork


class SQLAlchemyFeedbackUnitOfWork(FeedbackUnitOfWork):

    """SQLA implementation for unit of work."""

    def __init__(self, sqla_session: AsyncSession) -> None:
        self.session = sqla_session
        self.feedback_repo = SQLAlchemyFeedbackRepository(sqla_session)

    async def begin(self) -> None:
        await self.session.begin()

    async def commit(self) -> None:
        await self.session.commit()

    async def rollback(self) -> None:
        await self.session.rollback()

===== END FILE =====

===== FILE: src/infrastructure/sqlalchemy/group_google_calendar/__init__.py =====

===== END FILE =====

===== FILE: src/infrastructure/sqlalchemy/group_google_calendar/models.py =====
from __future__ import annotations

import datetime
import uuid

from sqlalchemy import text
from sqlalchemy.orm import Mapped, mapped_column

from src.domain.base_value_objects import UUID, LinkValueObject
from src.domain.group_google_calendar.entities import GroupGoogleCalendarEntity
from src.infrastructure.sqlalchemy.session import Base


class GroupGoogleCalendar(Base):

    """SQLAlchemy model of group google calendar."""

    __tablename__ = "group_google_calendars"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True)
    course_run_id: Mapped[uuid.UUID] = mapped_column(nullable=False)
    name: Mapped[str] = mapped_column(nullable=False)
    link: Mapped[str] = mapped_column(nullable=False)

    created_at: Mapped[datetime.datetime] = mapped_column(
        server_default=text("TIMEZONE('utc', now())"),
    )
    updated_at: Mapped[datetime.datetime] = mapped_column(
        server_default=text("TIMEZONE('utc', now())"),
        onupdate=datetime.datetime.utcnow,
    )

    @staticmethod
    def from_domain(group_calendar: GroupGoogleCalendarEntity) -> GroupGoogleCalendar:
        return GroupGoogleCalendar(
            id=uuid.UUID(group_calendar.id.value),
            course_run_id=uuid.UUID(group_calendar.course_run_id.value),
            name=group_calendar.name,
            link=group_calendar.link.value,
        )

    def to_domain(self) -> GroupGoogleCalendarEntity:
        return GroupGoogleCalendarEntity(
            id=UUID(str(self.id)),
            course_run_id=UUID(str(self.course_run_id)),
            name=self.name,
            link=LinkValueObject(self.link),
        )

===== END FILE =====

===== FILE: src/infrastructure/sqlalchemy/group_google_calendar/repository.py =====
from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import delete, select

from src.domain.group_google_calendar.exceptions import GroupGoogleCalendarNotFoundError
from src.domain.group_google_calendar.ggc_repository import IGroupGoogleCalendarRepository
from src.infrastructure.sqlalchemy.group_google_calendar.models import GroupGoogleCalendar

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

    from src.domain.base_value_objects import UUID
    from src.domain.group_google_calendar.entities import GroupGoogleCalendarEntity


class SQLAlchemyGroupGoogleCalendarRepository(IGroupGoogleCalendarRepository):

    """SQLAlchemy's implementation of Repository for group google calendar."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, group_google_calendar: GroupGoogleCalendarEntity) -> None:
        calendar_ = GroupGoogleCalendar.from_domain(group_google_calendar)
        self.session.add(calendar_)

    async def delete(self, group_google_calendar_id: UUID) -> None:
        delete_statement = (
            delete(GroupGoogleCalendar)
            .where(GroupGoogleCalendar.id == group_google_calendar_id.value)
        )
        result = await self.session.execute(delete_statement)
        if result.rowcount == 0:
            raise GroupGoogleCalendarNotFoundError

    async def get_all_by_course_run_id(self, course_run_id: UUID) -> list[GroupGoogleCalendarEntity]:
        query = (
            select(GroupGoogleCalendar)
            .filter_by(course_run_id=course_run_id.value)
            .order_by(GroupGoogleCalendar.created_at.desc())
        )
        result = await self.session.execute(query)
        feedbacks = result.unique().scalars().all()
        return [feedback.to_domain() for feedback in feedbacks]

===== END FILE =====

===== FILE: src/infrastructure/sqlalchemy/group_google_calendar/unit_of_work.py =====
from sqlalchemy.ext.asyncio import AsyncSession

from src.infrastructure.sqlalchemy.base_unit_of_work import SQLAlchemyUnitOfWork
from src.infrastructure.sqlalchemy.course_run.repository import SQLAlchemyCourseRunRepository
from src.infrastructure.sqlalchemy.courses.repository import SQLAlchemyCourseRepository
from src.infrastructure.sqlalchemy.group_google_calendar.repository import SQLAlchemyGroupGoogleCalendarRepository
from src.services.group_google_calendar.unit_of_work import GroupGoogleCalendarUnitOfWork


class SQLAlchemyGGCUnitOfWork(SQLAlchemyUnitOfWork, GroupGoogleCalendarUnitOfWork):

    """SQLA implementation for unit of work."""

    def __init__(self, sqla_session: AsyncSession) -> None:
        super().__init__(sqla_session)
        self.ggc_repo = SQLAlchemyGroupGoogleCalendarRepository(sqla_session)
        self.course_repo = SQLAlchemyCourseRepository(sqla_session)
        self.course_run_repo = SQLAlchemyCourseRunRepository(sqla_session)

===== END FILE =====

===== FILE: src/infrastructure/sqlalchemy/playlists/__init__.py =====

===== END FILE =====

===== FILE: src/infrastructure/sqlalchemy/playlists/models.py =====
from __future__ import annotations

import datetime
import uuid

from sqlalchemy import text
from sqlalchemy.orm import Mapped, mapped_column

from src.domain.base_value_objects import UUID, LinkValueObject
from src.domain.playlists.entities import PlaylistEntity
from src.domain.playlists.value_objects import VideoResourceType
from src.infrastructure.sqlalchemy.session import Base


class Playlist(Base):

    """SQLAlchemy model of Playlist."""

    __tablename__ = "playlists"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True)
    course_run_id: Mapped[uuid.UUID] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(nullable=False)
    type: Mapped[str] = mapped_column(nullable=False)
    link: Mapped[str] = mapped_column(nullable=False)

    created_at: Mapped[datetime.datetime] = mapped_column(
        server_default=text("TIMEZONE('utc', now())"),
    )
    updated_at: Mapped[datetime.datetime] = mapped_column(
        server_default=text("TIMEZONE('utc', now())"),
        onupdate=datetime.datetime.utcnow,
    )

    @staticmethod
    def from_domain(playlist: PlaylistEntity) -> Playlist:
        return Playlist(
            id=uuid.UUID(playlist.id.value),
            course_run_id=uuid.UUID(playlist.course_run_id.value),
            name=playlist.name,
            type=playlist.type.value,
            link=playlist.link.value,
        )

    def to_domain(self) -> PlaylistEntity:
        return PlaylistEntity(
            id=UUID(str(self.id)),
            course_run_id=UUID(str(self.course_run_id)),
            name=self.name,
            type=VideoResourceType(self.type),
            link=LinkValueObject(self.link),
        )

===== END FILE =====

===== FILE: src/infrastructure/sqlalchemy/playlists/repository.py =====
from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import delete, select, update

from src.domain.playlists.exceptions import PlaylistNotFoundError
from src.domain.playlists.playlist_repository import IPlaylistRepository
from src.infrastructure.sqlalchemy.playlists.models import Playlist

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

    from src.domain.base_value_objects import UUID
    from src.domain.playlists.entities import PlaylistEntity


class SQLAlchemyPlaylistRepository(IPlaylistRepository):

    """SQLAlchemy's implementation of Repository for Playlist."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, playlist: PlaylistEntity) -> None:
        playlist_ = Playlist.from_domain(playlist)
        self.session.add(playlist_)

    async def update(self, playlist: PlaylistEntity) -> None:
        playlist_ = Playlist.from_domain(playlist)
        update_statement = (
            update(Playlist)
            .where(Playlist.id == playlist_.id)
            .values(name=playlist_.name, link=playlist_.link, type=playlist_.type)
        )
        result = await self.session.execute(update_statement)
        if result.rowcount == 0:
            raise PlaylistNotFoundError

    async def delete(self, playlist_id: UUID) -> None:
        delete_statement = (
            delete(Playlist)
            .where(Playlist.id == playlist_id.value)
        )
        result = await self.session.execute(delete_statement)
        if result.rowcount == 0:
            raise PlaylistNotFoundError

    async def get_all_by_course_run_id(self, course_run_id: UUID) -> list[PlaylistEntity]:
        query = (
            select(Playlist)
            .filter_by(course_run_id=course_run_id.value)
            .order_by(Playlist.created_at.desc())
        )
        result = await self.session.execute(query)
        playlists = result.unique().scalars().all()
        return [playlist.to_domain() for playlist in playlists]

===== END FILE =====

===== FILE: src/infrastructure/sqlalchemy/playlists/unit_of_work.py =====
from sqlalchemy.ext.asyncio import AsyncSession

from src.infrastructure.sqlalchemy.base_unit_of_work import SQLAlchemyUnitOfWork
from src.infrastructure.sqlalchemy.course_run.repository import SQLAlchemyCourseRunRepository
from src.infrastructure.sqlalchemy.playlists.repository import SQLAlchemyPlaylistRepository
from src.services.playlists.unit_of_work import PlaylistUnitOfWork


class SQLAlchemyPlaylistUnitOfWork(SQLAlchemyUnitOfWork, PlaylistUnitOfWork):

    """SQLA implementation for unit of work."""

    def __init__(self, sqla_session: AsyncSession) -> None:
        super().__init__(sqla_session)
        self.playlist_repo = SQLAlchemyPlaylistRepository(sqla_session)
        self.course_run_repo = SQLAlchemyCourseRunRepository(sqla_session)

===== END FILE =====

===== FILE: src/infrastructure/sqlalchemy/talent_profile/__init__.py =====

===== END FILE =====

===== FILE: src/infrastructure/sqlalchemy/talent_profile/models.py =====
from __future__ import annotations

import datetime
import uuid

from sqlalchemy import text
from sqlalchemy.orm import Mapped, mapped_column

from src.domain.base_value_objects import UUID, EmptyLinkValueObject
from src.domain.talent_profile.entities import TalentProfileEntity
from src.infrastructure.sqlalchemy.session import Base


class TalentProfile(Base):

    """SQLAlchemy model of Talent profile."""

    __tablename__ = "talent_profiles"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True)
    image_url: Mapped[str] = mapped_column(nullable=True)
    location: Mapped[str] = mapped_column(nullable=False)
    position: Mapped[str] = mapped_column(nullable=False)
    company: Mapped[str] = mapped_column(nullable=False)
    link_ru_resume: Mapped[str] = mapped_column(nullable=False)
    link_eng_resume: Mapped[str] = mapped_column(nullable=False)
    link_tg_personal: Mapped[str] = mapped_column(nullable=False)
    link_linkedin: Mapped[str] = mapped_column(nullable=False)

    created_at: Mapped[datetime.datetime] = mapped_column(
        server_default=text("TIMEZONE('utc', now())"),
    )
    updated_at: Mapped[datetime.datetime] = mapped_column(
        server_default=text("TIMEZONE('utc', now())"),
        onupdate=datetime.datetime.utcnow,
    )

    @staticmethod
    def from_domain(profile: TalentProfileEntity) -> TalentProfile:
        return TalentProfile(
            id=uuid.UUID(profile.id.value),
            image_url=profile.image_url,
            location=profile.location,
            position=profile.position,
            company=profile.company,
            link_ru_resume=profile.link_ru_resume.value,
            link_eng_resume=profile.link_eng_resume.value,
            link_tg_personal=profile.link_tg_personal.value,
            link_linkedin=profile.link_linkedin.value,
        )

    def to_domain(self) -> TalentProfileEntity:
        return TalentProfileEntity(
            id=UUID(str(self.id)),
            image_url=self.image_url,
            location=self.location,
            position=self.position,
            company=self.company,
            link_ru_resume=EmptyLinkValueObject(self.link_ru_resume),
            link_eng_resume=EmptyLinkValueObject(self.link_eng_resume),
            link_tg_personal=EmptyLinkValueObject(self.link_tg_personal),
            link_linkedin=EmptyLinkValueObject(self.link_linkedin),
        )

===== END FILE =====

===== FILE: src/infrastructure/sqlalchemy/talent_profile/repository.py =====
from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import select
from sqlalchemy.exc import NoResultFound

from src.domain.talent_profile.exceptions import TalentProfileNotFoundError
from src.domain.talent_profile.profile_repository import ITalentProfileRepository
from src.infrastructure.sqlalchemy.talent_profile.models import TalentProfile

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

    from src.domain.base_value_objects import UUID
    from src.domain.talent_profile.entities import TalentProfileEntity


class SQLAlchemyTalentProfileRepository(ITalentProfileRepository):

    """SQLAlchemy's implementation of Repository for talent profile."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, profile: TalentProfileEntity) -> None:
        profile_ = TalentProfile.from_domain(profile)
        self.session.add(profile_)

    async def update(self, profile: TalentProfileEntity) -> None:
        profile_ = await self.__get_by_id(profile.id)
        profile_.image_url = profile.image_url
        profile_.location = profile.location
        profile_.position = profile.position
        profile_.company = profile.company
        profile_.link_ru_resume = profile.link_ru_resume.value
        profile_.link_eng_resume = profile.link_eng_resume.value
        profile_.link_tg_personal = profile.link_tg_personal.value
        profile_.link_linkedin = profile.link_linkedin.value

    async def delete(self, user_id: UUID) -> None:
        profile_ = await self.__get_by_id(user_id)
        await self.session.delete(profile_)

    async def get_by_user_id(self, user_id: UUID) -> TalentProfileEntity:
        profile_ = await self.__get_by_id(user_id)
        return profile_.to_domain()

    async def __get_by_id(self, user_id: UUID) -> TalentProfile:
        query = (
            select(TalentProfile)
            .filter_by(id=user_id.value)
        )
        try:
            result = await self.session.execute(query)
            return result.unique().scalars().one()
        except NoResultFound as ex:
            raise TalentProfileNotFoundError from ex

===== END FILE =====

===== FILE: src/infrastructure/sqlalchemy/talent_profile/unit_of_work.py =====
from sqlalchemy.ext.asyncio import AsyncSession

from src.infrastructure.sqlalchemy.base_unit_of_work import SQLAlchemyUnitOfWork
from src.infrastructure.sqlalchemy.talent_profile.repository import SQLAlchemyTalentProfileRepository
from src.infrastructure.sqlalchemy.users.repository import SQLAlchemyUserRepository
from src.services.talent_profile.unit_of_work import TalentProfileUnitOfWork


class SQLAlchemyTalentProfileUnitOfWork(SQLAlchemyUnitOfWork, TalentProfileUnitOfWork):

    """SQLA implementation for unit of work."""

    def __init__(self, sqla_session: AsyncSession) -> None:
        super().__init__(sqla_session)
        self.user_repo = SQLAlchemyUserRepository(sqla_session)
        self.profile_repo = SQLAlchemyTalentProfileRepository(sqla_session)

===== END FILE =====

===== FILE: src/infrastructure/sqlalchemy/timetable/__init__.py =====

===== END FILE =====

===== FILE: src/infrastructure/sqlalchemy/timetable/models.py =====
from __future__ import annotations

import datetime
import uuid

from sqlalchemy import text
from sqlalchemy.orm import Mapped, mapped_column

from src.domain.base_value_objects import UUID
from src.domain.timetable.entities import DayRuleEntity, WeekRuleEntity
from src.domain.timetable.value_objects import Weekday
from src.infrastructure.sqlalchemy.session import Base


class TimetableRule(Base):

    """SQLAlchemy model of Rule."""

    __tablename__ = "timetable_rules"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True)
    rule_type: Mapped[str] = mapped_column(nullable=False)
    start_time: Mapped[datetime.time] = mapped_column(nullable=False)
    end_time: Mapped[datetime.time] = mapped_column(nullable=False)
    start_period_date: Mapped[datetime.date] = mapped_column(nullable=False)
    end_period_date: Mapped[datetime.date] = mapped_column(nullable=False)
    weekdays: Mapped[str] = mapped_column(nullable=True)

    course_run_id: Mapped[uuid.UUID] = mapped_column(nullable=False)

    created_at: Mapped[datetime.datetime] = mapped_column(
        server_default=text("TIMEZONE('utc', now())"),
    )
    updated_at: Mapped[datetime.datetime] = mapped_column(
        server_default=text("TIMEZONE('utc', now())"),
        onupdate=datetime.datetime.utcnow,
    )

    @staticmethod
    def from_domain(rule: DayRuleEntity | WeekRuleEntity) -> TimetableRule:
        if isinstance(rule, DayRuleEntity):
            return TimetableRule(
                id=rule.id.value,
                course_run_id=rule.timetable_id.value,
                rule_type="day",
                start_time=rule.start_time,
                end_time=rule.end_time,
                start_period_date=rule.date,
                end_period_date=rule.date,
                weekdays="",
            )
        return TimetableRule(
            id=rule.id.value,
            course_run_id=rule.timetable_id.value,
            rule_type="week",
            start_time=rule.start_time,
            end_time=rule.end_time,
            start_period_date=rule.start_period_date,
            end_period_date=rule.end_period_date,
            weekdays=",".join([weekday.value for weekday in rule.weekdays]),
        )

    def to_domain(self) -> DayRuleEntity | WeekRuleEntity:
        if self.rule_type == "day":
            return DayRuleEntity(
                id=UUID(str(self.id)),
                timetable_id=UUID(str(self.course_run_id)),
                start_time=self.start_time,
                end_time=self.end_time,
                date=self.start_period_date,
            )
        return WeekRuleEntity(
            id=UUID(str(self.id)),
            timetable_id=UUID(str(self.course_run_id)),
            start_time=self.start_time,
            end_time=self.end_time,
            start_period_date=self.start_period_date,
            end_period_date=self.end_period_date,
            weekdays=[Weekday(weekday) for weekday in self.weekdays.split(",") if weekday != ""],
        )

===== END FILE =====

===== FILE: src/infrastructure/sqlalchemy/timetable/repository.py =====
from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import select
from sqlalchemy.exc import NoResultFound

from src.domain.timetable.entities import DayRuleEntity, TimetableEntity, WeekRuleEntity
from src.domain.timetable.exceptions import IncorrectRuleTypeError, RuleNotFoundError
from src.domain.timetable.timetable_repository import ITimetableRepository
from src.infrastructure.sqlalchemy.timetable.models import TimetableRule

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

    from src.domain.base_value_objects import UUID


class SQLAlchemyTimetableRepository(ITimetableRepository):

    """SQLAlchemy's implementation of Repository for Timetable."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_id(self, course_run_id: UUID) -> TimetableEntity:
        query = (
            select(TimetableRule)
            .filter_by(course_run_id=course_run_id.value)
        )
        result = await self.session.execute(query)
        timetable_rules = result.scalars().all()
        return TimetableEntity(
            id=course_run_id,
            course_run_id=course_run_id,
            rules=[rule.to_domain() for rule in timetable_rules],
        )

    async def create_rule(self, rule: DayRuleEntity | WeekRuleEntity) -> None:
        rule_ = TimetableRule.from_domain(rule)
        self.session.add(rule_)

    async def update_rule(self, rule: DayRuleEntity | WeekRuleEntity) -> None:
        rule_ = await self.__get_by_rule_id(rule.id)
        rule_.start_time = rule.start_time
        rule_.end_time = rule.end_time
        if isinstance(rule, DayRuleEntity) and rule_.rule_type == "day":
            rule_.start_period_date = rule.date
            rule_.end_period_date = rule.date
            rule_.weekdays = ""
        elif isinstance(rule, WeekRuleEntity) and rule_.rule_type == "week":
            rule_.start_period_date = rule.start_period_date
            rule_.end_period_date = rule.end_period_date
            rule_.weekdays = ",".join([weekday.value for weekday in rule.weekdays])
        else:
            raise IncorrectRuleTypeError

    async def delete_rule(self, rule_id: UUID) -> None:
        rule_ = await self.__get_by_rule_id(rule_id)
        await self.session.delete(rule_)

    async def __get_by_rule_id(self, rule_id: UUID) -> TimetableRule:
        query = (
            select(TimetableRule)
            .filter_by(id=rule_id.value)
        )
        try:
            result = await self.session.execute(query)
            return result.unique().scalars().one()
        except NoResultFound as ex:
            raise RuleNotFoundError from ex

===== END FILE =====

===== FILE: src/infrastructure/sqlalchemy/timetable/unit_of_work.py =====
from sqlalchemy.ext.asyncio import AsyncSession

from src.infrastructure.sqlalchemy.base_unit_of_work import SQLAlchemyUnitOfWork
from src.infrastructure.sqlalchemy.timetable.repository import SQLAlchemyTimetableRepository
from src.services.timetable.unit_of_work import TimetableUnitOfWork


class SQLAlchemyTimetableUnitOfWork(SQLAlchemyUnitOfWork, TimetableUnitOfWork):

    """SQLA implementation for unit of work."""

    def __init__(self, sqla_session: AsyncSession) -> None:
        super().__init__(sqla_session)
        self.timetable_repo = SQLAlchemyTimetableRepository(sqla_session)

===== END FILE =====

===== FILE: src/infrastructure/sqlalchemy/users/__init__.py =====

===== END FILE =====

===== FILE: src/infrastructure/sqlalchemy/users/models.py =====
import datetime
import uuid

from sqlalchemy import text
from sqlalchemy.orm import Mapped, mapped_column

from src.domain.auth.entities import UserEntity
from src.domain.auth.value_objects import Email, PartOfName, UserRole
from src.domain.base_value_objects import UUID
from src.infrastructure.sqlalchemy.session import Base


class User(Base):

    """SQLAlchemy model of User."""

    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True)
    firstname: Mapped[str] = mapped_column(nullable=False)
    lastname: Mapped[str] = mapped_column(nullable=False)
    role: Mapped[str] = mapped_column(nullable=False)
    email: Mapped[str] = mapped_column(unique=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(
        server_default=text("TIMEZONE('utc', now())"),
    )
    updated_at: Mapped[datetime.datetime] = mapped_column(
        server_default=text("TIMEZONE('utc', now())"),
        onupdate=datetime.datetime.utcnow,
    )

    def to_domain(self) -> UserEntity:
        return UserEntity(
            id=UUID(str(self.id)),
            firstname=PartOfName(self.firstname),
            lastname=PartOfName(self.lastname),
            role=UserRole(self.role),
            email=Email(self.email),
            hashed_password=self.hashed_password,
        )

    @staticmethod
    def from_domain(user: UserEntity) -> "User":
        return User(
            id=user.id.value,
            firstname=user.firstname.value,
            lastname=user.lastname.value,
            role=user.role.value,
            email=user.email.value,
            hashed_password=user.hashed_password,
        )

===== END FILE =====

===== FILE: src/infrastructure/sqlalchemy/users/repository.py =====
from sqlalchemy import select
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.auth.entities import UserEntity
from src.domain.auth.exceptions import UserNotFoundError
from src.domain.auth.user_repository import IUserRepository
from src.domain.auth.value_objects import Email
from src.domain.base_value_objects import UUID
from src.infrastructure.sqlalchemy.users.models import User


class SQLAlchemyUserRepository(IUserRepository):

    """SqlAlchemy implementation of Repository for User."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, user: UserEntity) -> None:
        user_ = User.from_domain(user)
        self.session.add(user_)

    async def update(self, user: UserEntity) -> None:
        user_ = await self.__get_by_field(id=user.id.value)
        user_.firstname = user.firstname.value
        user_.lastname = user.lastname.value
        user_.email = user.email.value
        user_.hashed_password = user.hashed_password

    async def delete(self, user_id: UUID) -> None:
        user_ = await self.__get_by_field(id=user_id.value)
        await self.session.delete(user_)

    async def get_by_id(self, user_id: UUID) -> UserEntity:
        user = await self.__get_by_field(id=user_id.value)
        return user.to_domain()

    async def get_by_email(self, email: Email) -> UserEntity:
        user = await self.__get_by_field(email=email.value)
        return user.to_domain()

    async def __get_by_field(self, **kwargs) -> User:
        try:
            result = await self.session.execute(select(User).filter_by(**kwargs))
            return result.scalars().one()
        except NoResultFound:
            raise UserNotFoundError from NoResultFound

===== END FILE =====

===== FILE: src/infrastructure/sqlalchemy/users/unit_of_work.py =====
from sqlalchemy.ext.asyncio import AsyncSession

from src.infrastructure.sqlalchemy.talent_profile.repository import SQLAlchemyTalentProfileRepository
from src.infrastructure.sqlalchemy.users.repository import SQLAlchemyUserRepository
from src.services.auth.unit_of_work import AuthUnitOfWork


class SQLAlchemyAuthUnitOfWork(AuthUnitOfWork):

    """SQLA implementation for unit of work."""

    def __init__(self, sqla_session: AsyncSession) -> None:
        self.session = sqla_session
        self.user_repo = SQLAlchemyUserRepository(sqla_session)
        self.profile_repo = SQLAlchemyTalentProfileRepository(sqla_session)

    async def begin(self) -> None:
        await self.session.begin()

    async def commit(self) -> None:
        await self.session.commit()

    async def rollback(self) -> None:
        await self.session.rollback()

===== END FILE =====

===== FILE: src/services/__init__.py =====

===== END FILE =====

===== FILE: src/services/base_unit_of_work.py =====
from abc import ABC, abstractmethod


class ServiceUnitOfWork(ABC):

    """Base class implemented pattern Unit of Work."""

    @abstractmethod
    async def begin(self) -> None:
        raise NotImplementedError

    @abstractmethod
    async def commit(self) -> None:
        raise NotImplementedError

    @abstractmethod
    async def rollback(self) -> None:
        raise NotImplementedError

===== END FILE =====

===== FILE: src/services/auth/__init__.py =====

===== END FILE =====

===== FILE: src/services/auth/command_service.py =====
import re
import uuid

from sqlalchemy.exc import IntegrityError

from src.domain.auth.constants import TALENT_ROLE
from src.domain.auth.entities import UserEntity
from src.domain.auth.exceptions import UserWithEmailExistsError
from src.domain.auth.value_objects import Email, PartOfName, UserRole
from src.domain.base_value_objects import UUID
from src.domain.talent_profile.entities import TalentProfileEntity
from src.domain.talent_profile.exceptions import TalentProfileAlreadyExistsError
from src.infrastructure.security.password_service import PasswordService
from src.services.auth.session_service import SessionService
from src.services.auth.unit_of_work import AuthUnitOfWork


class AuthCommandService:

    """Class implemented CQRS pattern, command class."""

    def __init__(self, uow: AuthUnitOfWork, session_service: SessionService) -> None:
        self.uow = uow
        self.session_service = session_service

    async def register_talent(self, firstname_: str, lastname_: str, email_: str, password_: str) -> str:
        user_id = UUID(str(uuid.uuid4()))
        firstname = PartOfName(firstname_)
        lastname = PartOfName(lastname_)
        role = UserRole(TALENT_ROLE)
        email = Email(email_)
        PasswordService.validate_password(password_)
        hashed_password = PasswordService.create_hashed_password(password_)
        user = UserEntity(user_id, firstname, lastname, role, email, hashed_password)
        auth_token = str(uuid.uuid4())
        profile = TalentProfileEntity(user_id)
        try:
            await self.uow.user_repo.create(user)
            await self.uow.profile_repo.create(profile)
            await self.uow.commit()
        except IntegrityError as ex:
            await self.uow.rollback()
            table_name = re.search(r"INSERT INTO (\w+)", ex.statement).group(1)
            if table_name == "users":
                raise UserWithEmailExistsError from ex
            raise TalentProfileAlreadyExistsError from ex
        await self.session_service.set(auth_token, user)
        return auth_token

    async def login(self, email_: str, password_: str) -> str:
        email = Email(email_)
        auth_token = str(uuid.uuid4())
        user = await self.uow.user_repo.get_by_email(email)
        PasswordService.verify_password(password_, user.hashed_password)
        await self.session_service.set(auth_token, user)
        return auth_token

    async def logout(self, auth_token: str) -> None:
        await self.session_service.delete(auth_token)

    async def me(self, auth_token: str) -> UserEntity:
        return await self.session_service.get(auth_token)

===== END FILE =====

===== FILE: src/services/auth/session_service.py =====
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.domain.auth.entities import UserEntity


class SessionService(ABC):

    """Base class for session as service."""

    @abstractmethod
    async def get(self, auth_token: str) -> UserEntity:
        raise NotImplementedError

    @abstractmethod
    async def update(self, auth_token: str, user: UserEntity) -> None:
        raise NotImplementedError

    @abstractmethod
    async def set(self, auth_token: str, user: UserEntity) -> None:
        raise NotImplementedError

    @abstractmethod
    async def delete(self, auth_token: str) -> None:
        raise NotImplementedError

===== END FILE =====

===== FILE: src/services/auth/unit_of_work.py =====
from abc import ABC, abstractmethod

from src.domain.auth.user_repository import IUserRepository
from src.domain.talent_profile.profile_repository import ITalentProfileRepository


class AuthUnitOfWork(ABC):

    """Base class implemented pattern Unit of Work."""

    user_repo: IUserRepository
    profile_repo: ITalentProfileRepository

    @abstractmethod
    async def begin(self) -> None:
        raise NotImplementedError

    @abstractmethod
    async def commit(self) -> None:
        raise NotImplementedError

    @abstractmethod
    async def rollback(self) -> None:
        raise NotImplementedError

===== END FILE =====

===== FILE: src/services/course_run/__init__.py =====

===== END FILE =====

===== FILE: src/services/course_run/command_service.py =====
from __future__ import annotations

import datetime
import uuid
from typing import TYPE_CHECKING

from sqlalchemy.exc import IntegrityError

from src.domain.base_value_objects import UUID
from src.domain.course_run.entities import CourseRunEntity
from src.domain.course_run.exceptions import CourseRunAlreadyExistsError, NoActualCourseRunError
from src.domain.courses.value_objects import CourseRun
from src.domain.timetable.exceptions import NoActualTimetableError

if TYPE_CHECKING:
    from src.domain.group_google_calendar.entities import GroupGoogleCalendarEntity
    from src.domain.timetable.entities import TimetableEntity
    from src.services.course_run.unit_of_work import CourseRunUnitOfWork


class CourseRunCommandService:

    """Class implemented CQRS pattern, command class."""

    def __init__(self, uow: CourseRunUnitOfWork) -> None:
        self.uow = uow

    async def create_course_run(self, course_id: str, season: str, year: int) -> str:
        course_run_id = UUID(str(uuid.uuid4()))
        course_id = UUID(course_id)
        course_run_name = CourseRun(f"{season} {year}")
        course_run = CourseRunEntity(course_run_id, course_id, course_run_name)
        try:
            await self.uow.course_run_repo.create(course_run)
            await self.uow.commit()
        except IntegrityError as ex:
            await self.uow.rollback()
            raise CourseRunAlreadyExistsError from ex
        except Exception:
            await self.uow.rollback()
            raise
        return course_run_id.value

    async def delete_course_run(self, course_run_id: str) -> None:
        course_run_id = UUID(course_run_id)
        try:
            await self.uow.course_run_repo.delete(course_run_id)
            timetable = await self.uow.timetable_repo.get_by_id(course_run_id)
            for rule in timetable.rules:
                await self.uow.timetable_repo.delete_rule(rule.id)
            await self.uow.commit()
        except Exception:
            await self.uow.rollback()
            raise

    async def get_course_run_by_id(self, course_run_id: str) -> CourseRunEntity:
        course_run_id = UUID(course_run_id)
        return await self.uow.course_run_repo.get_by_id(course_run_id)

    async def get_all_course_runs_by_id(self, course_id: str) -> list[CourseRunEntity]:
        course_id = UUID(course_id)
        return await self.uow.course_run_repo.get_all_by_course_id(course_id)

    async def get_actual_timetable_by_id(
            self, course_id: str,
    ) -> tuple[TimetableEntity, CourseRunEntity, list[GroupGoogleCalendarEntity]]:
        current_date = datetime.datetime.now().date()
        course_id = UUID(course_id)
        course_runs = await self.uow.course_run_repo.get_all_by_course_id(course_id)
        for course_run in course_runs:
            if course_run.is_actual_by_date(current_date):
                error_message = "Для актуального запуска еще не создано расписание"
                timetable = await self.uow.timetable_repo.get_by_id(course_run.id)
                google_timetable_groups = await self.uow.ggc_repo.get_all_by_course_run_id(course_run.id)
                if not timetable.lessons and not google_timetable_groups:
                    raise NoActualTimetableError(error_message=error_message)
                return timetable, course_run, google_timetable_groups
        raise NoActualCourseRunError

===== END FILE =====

===== FILE: src/services/course_run/unit_of_work.py =====
from abc import ABC

from src.domain.course_run.course_run_repository import ICourseRunRepository
from src.domain.group_google_calendar.ggc_repository import IGroupGoogleCalendarRepository
from src.domain.timetable.timetable_repository import ITimetableRepository
from src.services.base_unit_of_work import ServiceUnitOfWork


class CourseRunUnitOfWork(ServiceUnitOfWork, ABC):

    """Base class implemented pattern Unit of Work."""

    course_run_repo: ICourseRunRepository
    timetable_repo: ITimetableRepository
    ggc_repo: IGroupGoogleCalendarRepository

===== END FILE =====

===== FILE: src/services/courses/__init__.py =====

===== END FILE =====

===== FILE: src/services/courses/command_service.py =====
from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from sqlalchemy.exc import IntegrityError

from src.domain.base_value_objects import UUID
from src.domain.courses.entities import CourseEntity
from src.domain.courses.exceptions import CourseAlreadyExistsError, CourseNotFoundError
from src.domain.courses.value_objects import (
    Author,
    CourseName,
    CourseRun,
    Format,
    Implementer,
    Period,
    Resource,
    Role,
    Terms,
)

if TYPE_CHECKING:
    from src.services.courses.unit_of_work import CoursesUnitOfWork


class CourseCommandService:

    """Class implemented CQRS pattern, command class."""

    def __init__(self, uow: CoursesUnitOfWork) -> None:
        self.uow = uow

    async def create_course(self, name_: str) -> str:
        course_id = UUID(str(uuid.uuid4()))
        name = CourseName(name_)
        course = CourseEntity(course_id, name)
        try:
            await self.uow.course_repo.create(course)
            await self.uow.commit()
        except IntegrityError as ex:
            await self.uow.rollback()
            raise CourseAlreadyExistsError from ex
        except Exception:
            await self.uow.rollback()
            raise
        return course_id.value

    async def update_course(
            self, course_id: str, name_: str, image_url: str | None, limits_: int | None,
            prerequisites_: str | None, description_: str | None, topics_: str | None,
            assessment_: str | None, resources_: list[dict[str, str]], extra_: str | None,
            author_: str | None, implementer_: str | None, format_: str | None,
            terms_: str | None, roles: list[str], periods: list[str], runs: list[str],
    ) -> None:
        course = CourseEntity(
            id=UUID(str(course_id)),
            name=CourseName(name_),
            image_url=image_url,
            limits=limits_,
            prerequisites=prerequisites_,
            description=description_,
            topics=topics_,
            assessment=assessment_,
            resources=[Resource(title=res["title"], link=res["link"]) for res in resources_],
            extra=extra_,
            author=Author(author_) if author_ else None,
            implementer=Implementer(implementer_) if implementer_ else None,
            format=Format(format_) if format_ else None,
            terms=Terms(terms_) if terms_ else None,
            roles=[Role(role) for role in roles],
            periods=[Period(period) for period in periods],
            last_runs=[CourseRun(run) for run in runs],
        )
        try:
            await self.uow.course_repo.update(course)
            await self.uow.commit()
        except IntegrityError as ex:
            await self.uow.rollback()
            raise CourseAlreadyExistsError from ex
        except CourseNotFoundError:
            await self.uow.rollback()
            raise

    async def delete_course(self, course_id: str) -> None:
        course_id = UUID(course_id)
        try:
            await self.uow.course_repo.delete(course_id)
            await self.uow.commit()
        except CourseNotFoundError:
            await self.uow.rollback()
            raise

    async def publish_course(self, course_id: str) -> None:
        course_id = UUID(course_id)
        try:
            course = await self.uow.course_repo.get_by_id(course_id)
            course.publish()
            await self.uow.course_repo.update_draft_status(course)
            await self.uow.commit()
        except CourseNotFoundError:
            await self.uow.rollback()
            raise

    async def hide_course(self, course_id: str) -> None:
        course_id = UUID(course_id)
        try:
            course = await self.uow.course_repo.get_by_id(course_id)
            course.hide()
            await self.uow.course_repo.update_draft_status(course)
            await self.uow.commit()
        except CourseNotFoundError:
            await self.uow.rollback()
            raise

===== END FILE =====

===== FILE: src/services/courses/course_cache_service.py =====
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.domain.base_value_objects import UUID
    from src.domain.courses.entities import CourseEntity


class CourseCacheService(ABC):

    """Base class for cache of course as service."""

    @abstractmethod
    async def get_one(self, course_id: UUID) -> CourseEntity | None:
        raise NotImplementedError

    @abstractmethod
    async def delete_one(self, course_id: UUID) -> None:
        raise NotImplementedError

    @abstractmethod
    async def set_one(self, course: CourseEntity) -> None:
        raise NotImplementedError

    @abstractmethod
    async def get_many(self) -> list[CourseEntity] | None:
        raise NotImplementedError

    @abstractmethod
    async def delete_many(self) -> None:
        raise NotImplementedError

    @abstractmethod
    async def set_many(self, courses: list[CourseEntity]) -> None:
        raise NotImplementedError

===== END FILE =====

===== FILE: src/services/courses/query_service_for_admin.py =====
from __future__ import annotations

from typing import TYPE_CHECKING

from src.domain.base_value_objects import UUID

if TYPE_CHECKING:
    from src.domain.courses.course_repository import ICourseRepository
    from src.domain.courses.entities import CourseEntity
    from src.services.courses.course_cache_service import CourseCacheService


class AdminCourseQueryService:

    """Class implemented CQRS pattern, query class for admin."""

    def __init__(self, course_repo: ICourseRepository, course_cache_service: CourseCacheService) -> None:
        self.course_repo = course_repo
        self.course_cache_service = course_cache_service

    async def get_course(self, course_id: str) -> CourseEntity:
        course_id = UUID(course_id)
        course_from_cache = await self.course_cache_service.get_one(course_id)
        if course_from_cache:
            return course_from_cache
        course = await self.course_repo.get_by_id(course_id)
        await self.course_cache_service.set_one(course)
        return course

    async def get_courses(self) -> list[CourseEntity]:
        courses_from_cache = await self.course_cache_service.get_many()
        if courses_from_cache:
            return courses_from_cache
        courses = await self.course_repo.get_all()
        await self.course_cache_service.set_many(courses)
        return courses

    async def invalidate_course(self, course_id: str) -> None:
        await self.course_cache_service.delete_one(UUID(course_id))
        await self.course_cache_service.delete_many()

===== END FILE =====

===== FILE: src/services/courses/query_service_for_talent.py =====
from __future__ import annotations

import datetime
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from src.domain.base_value_objects import UUID
from src.domain.courses.exceptions import CourseNotFoundError

if TYPE_CHECKING:
    from src.domain.courses.course_repository import ICourseRepository
    from src.domain.courses.entities import CourseEntity
    from src.services.courses.course_cache_service import CourseCacheService


@dataclass
class CourseFilter:

    """Class for filters on courses."""

    implementers: list[str] | None = field(default=None)
    formats: list[str] | None = field(default=None)
    terms: list[str] | None = field(default=None)
    roles: list[str] | None = field(default=None)
    query: str | None = field(default=None)
    only_actual: bool = field(default=False)


class TalentCourseQueryService:

    """Class implemented CQRS pattern, query class for talent."""

    def __init__(self, course_repo: ICourseRepository, course_cache_service: CourseCacheService) -> None:
        self.course_repo = course_repo
        self.course_cache_service = course_cache_service

    async def get_course(self, course_id: str) -> CourseEntity:
        course_id = UUID(course_id)
        course_from_cache = await self.course_cache_service.get_one(course_id)
        if course_from_cache and not course_from_cache.is_draft:
            return course_from_cache
        course = await self.course_repo.get_by_id(course_id)
        if course.is_draft:
            raise CourseNotFoundError
        await self.course_cache_service.set_one(course)
        return course

    async def get_courses(self, filters: CourseFilter) -> list[CourseEntity]:
        actual_run = self.__get_actual_run()
        courses_from_cache = await self.course_cache_service.get_many()
        if courses_from_cache:
            return [
                course for course in courses_from_cache
                if not course.is_draft and self.__matched(course, filters, actual_run)
            ]
        courses = await self.course_repo.get_all()
        courses = [course for course in courses if not course.is_draft]
        await self.course_cache_service.set_many(courses)
        return [course for course in courses if self.__matched(course, filters, actual_run)]

    async def invalidate_course(self, course_id: str) -> None:
        await self.course_cache_service.delete_one(UUID(course_id))
        await self.course_cache_service.delete_many()

    @staticmethod
    def __matched(course: CourseEntity, filters: CourseFilter, actual_run: str) -> bool:
        if filters.roles and not set(filters.roles).intersection({r.value for r in course.roles}):
            return False
        if filters.implementers and course.implementer.value not in filters.implementers:
            return False
        if filters.terms and not set(filters.terms).intersection(set(course.terms.value.split(", "))):
            return False
        if filters.formats and course.format.value not in filters.formats:
            return False
        if filters.query and filters.query.lower() not in course.name.value.lower():
            return False
        return not filters.only_actual or actual_run in {run.value for run in course.last_runs}

    @staticmethod
    def __get_actual_run() -> str:
        current_date = datetime.datetime.now().date()
        month, year = current_date.month, current_date.year
        if month in (8, 9, 10, 11, 12):
            return f"{'Осень'} {year}"
        return f"{'Весна'} {year}"

===== END FILE =====

===== FILE: src/services/courses/unit_of_work.py =====
from abc import ABC, abstractmethod

from src.domain.auth.user_repository import IUserRepository
from src.domain.courses.course_repository import ICourseRepository


class CoursesUnitOfWork(ABC):

    """Base class implemented pattern Unit of Work."""

    user_repo: IUserRepository
    course_repo: ICourseRepository

    @abstractmethod
    async def begin(self) -> None:
        raise NotImplementedError

    @abstractmethod
    async def commit(self) -> None:
        raise NotImplementedError

    @abstractmethod
    async def rollback(self) -> None:
        raise NotImplementedError

===== END FILE =====

===== FILE: src/services/favorite_courses/__init__.py =====

===== END FILE =====

===== FILE: src/services/favorite_courses/command_service.py =====
from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from sqlalchemy.exc import IntegrityError

from src.domain.base_value_objects import UUID
from src.domain.favorite_courses.entities import FavoriteCourseEntity
from src.domain.favorite_courses.exceptions import (
    CourseAlreadyExistsInFavoritesError,
    CourseDoesntExistInFavoritesError,
)

if TYPE_CHECKING:
    from src.services.favorite_courses.unit_of_work import FavoriteCoursesUnitOfWork


class FavoriteCoursesCommandService:

    """Class implemented CQRS pattern, command class."""

    def __init__(self, uow: FavoriteCoursesUnitOfWork) -> None:
        self.uow = uow

    async def add_course_to_favorites(self, user_id: str, course_id: str) -> None:
        favorite_course_id = UUID(str(uuid.uuid4()))
        user_id = UUID(user_id)
        course_id = UUID(course_id)
        favorite_course = FavoriteCourseEntity(favorite_course_id, user_id, course_id)
        try:
            await self.uow.favorites_repo.add_one(favorite_course)
            await self.uow.commit()
        except IntegrityError as ex:
            await self.uow.rollback()
            raise CourseAlreadyExistsInFavoritesError from ex
        except Exception:
            await self.uow.rollback()
            raise

    async def remove_course_from_favorites(self, favorite_course_id: str) -> None:
        favorite_course_id = UUID(favorite_course_id)
        try:
            await self.uow.favorites_repo.delete_one(favorite_course_id)
            await self.uow.commit()
        except Exception:
            await self.uow.rollback()
            raise

    async def course_in_favorites(self, course_id: str, user_id: str) -> bool:
        course_id = UUID(course_id)
        user_id = UUID(user_id)
        try:
            await self.uow.favorites_repo.get_one_by_course_id_and_user_id(course_id, user_id)
        except CourseDoesntExistInFavoritesError:
            return False
        else:
            return True

    async def get_favorite_courses(self, user_id: str) -> list[FavoriteCourseEntity]:
        user_id = UUID(user_id)
        return await self.uow.favorites_repo.get_all_by_user_id(user_id)

===== END FILE =====

===== FILE: src/services/favorite_courses/unit_of_work.py =====
from abc import ABC

from src.domain.courses.course_repository import ICourseRepository
from src.domain.favorite_courses.favorite_courses_repository import IFavoriteCourseRepository
from src.services.base_unit_of_work import ServiceUnitOfWork


class FavoriteCoursesUnitOfWork(ServiceUnitOfWork, ABC):

    """Base class implemented pattern Unit of Work."""

    course_repo: ICourseRepository
    favorites_repo: IFavoriteCourseRepository

===== END FILE =====

===== FILE: src/services/feedback/__init__.py =====

===== END FILE =====

===== FILE: src/services/feedback/command_service.py =====
from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from src.domain.base_value_objects import UUID
from src.domain.feedback.entities import FeedbackEntity
from src.domain.feedback.exceptions import FeedbackBelongsToAnotherUserError, FeedbackNotFoundError
from src.domain.feedback.value_objects import FeedbackText, Rating

if TYPE_CHECKING:
    from src.services.feedback.unit_of_work import FeedbackUnitOfWork


class FeedbackCommandService:

    """Class implemented CQRS pattern, command class."""

    def __init__(self, uow: FeedbackUnitOfWork) -> None:
        self.uow = uow

    async def create_feedback(self, course_id: str, author_id: str, text_: str, rating_: int) -> str:
        feedback_id = UUID(str(uuid.uuid4()))
        course_id = UUID(course_id)
        author_id = UUID(author_id)
        text = FeedbackText(text_)
        rating = Rating(rating_)
        feedback = FeedbackEntity(feedback_id, course_id, author_id, text, rating)
        try:
            await self.uow.feedback_repo.create(feedback)
            await self.uow.commit()
        except Exception:
            await self.uow.rollback()
            raise
        return feedback_id.value

    async def vote(self, feedback_id: str, user_id: str, vote_type: str) -> None:
        try:
            feedback = await self.uow.feedback_repo.get_one_by_id(UUID(feedback_id))
            feedback.vote(UUID(user_id), vote_type)
            await self.uow.feedback_repo.update_votes(feedback)
            await self.uow.commit()
        except FeedbackNotFoundError:
            await self.uow.rollback()
            raise

    async def unvote(self, feedback_id: str, user_id: str) -> None:
        try:
            feedback = await self.uow.feedback_repo.get_one_by_id(UUID(feedback_id))
            feedback.unvote(UUID(user_id))
            await self.uow.feedback_repo.update_votes(feedback)
            await self.uow.commit()
        except FeedbackNotFoundError:
            await self.uow.rollback()
            raise

    async def delete_feedback(self, feedback_id: str, user_id: str) -> None:
        feedback_id = UUID(feedback_id)
        user_id = UUID(user_id)
        try:
            feedback = await self.uow.feedback_repo.get_one_by_id(feedback_id)
            if feedback.author_id != user_id:
                raise FeedbackBelongsToAnotherUserError
            await self.uow.feedback_repo.delete(feedback_id)
            await self.uow.commit()
        except FeedbackNotFoundError:
            await self.uow.rollback()
            raise

===== END FILE =====

===== FILE: src/services/feedback/feedback_cache_service.py =====
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.domain.base_value_objects import UUID
    from src.domain.feedback.entities import FeedbackEntity


class FeedbackCacheService(ABC):

    """Base class for cache of feedback as service."""

    @abstractmethod
    async def get_many_by_course_id(self, course_id: UUID) -> list[FeedbackEntity] | None:
        raise NotImplementedError

    @abstractmethod
    async def delete_many(self, course_id: UUID) -> None:
        raise NotImplementedError

    @abstractmethod
    async def set_many(self, course_id: UUID, feedbacks: list[FeedbackEntity]) -> None:
        raise NotImplementedError

===== END FILE =====

===== FILE: src/services/feedback/query_service.py =====
from __future__ import annotations

from typing import TYPE_CHECKING

from src.domain.base_value_objects import UUID

if TYPE_CHECKING:
    from src.domain.feedback.entities import FeedbackEntity
    from src.domain.feedback.feedback_repository import IFeedbackRepository
    from src.services.feedback.feedback_cache_service import FeedbackCacheService


class FeedbackQueryService:

    """Class implemented CQRS pattern, query class."""

    def __init__(self, feedback_repo: IFeedbackRepository, feedback_cache_service: FeedbackCacheService) -> None:
        self.feedback_repo = feedback_repo
        self.feedback_cache_service = feedback_cache_service

    async def get_feedbacks_by_course_id(self, course_id: str) -> list[FeedbackEntity]:
        course_id = UUID(course_id)
        feedbacks_from_cache = await self.feedback_cache_service.get_many_by_course_id(course_id)
        if feedbacks_from_cache is not None:
            return feedbacks_from_cache
        feedbacks = await self.feedback_repo.get_all_by_course_id(course_id)
        await self.feedback_cache_service.set_many(course_id, feedbacks)
        return feedbacks

    async def invalidate_course(self, course_id: str) -> None:
        await self.feedback_cache_service.delete_many(UUID(course_id))

===== END FILE =====

===== FILE: src/services/feedback/unit_of_work.py =====
from abc import ABC, abstractmethod

from src.domain.feedback.feedback_repository import IFeedbackRepository


class FeedbackUnitOfWork(ABC):

    """Base class implemented pattern Unit of Work."""

    feedback_repo: IFeedbackRepository

    @abstractmethod
    async def begin(self) -> None:
        raise NotImplementedError

    @abstractmethod
    async def commit(self) -> None:
        raise NotImplementedError

    @abstractmethod
    async def rollback(self) -> None:
        raise NotImplementedError

===== END FILE =====

===== FILE: src/services/group_google_calendar/__init__.py =====

===== END FILE =====

===== FILE: src/services/group_google_calendar/command_service.py =====
from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from sqlalchemy.exc import SQLAlchemyError

from src.domain.base_exceptions import DomainError
from src.domain.base_value_objects import UUID, LinkValueObject
from src.domain.courses.value_objects import CourseName
from src.domain.group_google_calendar.entities import GroupGoogleCalendarEntity
from src.services.group_google_calendar.dto import UpdateGroupDTO, UpdateGroupGoogleCalendarDTO

if TYPE_CHECKING:
    from src.domain.course_run.entities import CourseRunEntity
    from src.services.group_google_calendar.unit_of_work import GroupGoogleCalendarUnitOfWork


class GroupGoogleCalendarCommandService:

    """Class implemented CQRS pattern, command class."""

    def __init__(self, uow: GroupGoogleCalendarUnitOfWork) -> None:
        self.uow = uow

    async def create(self, course_run_id: str, name: str, link: str) -> None:
        ggc_id = UUID(str(uuid.uuid4()))
        course_run_id = UUID(course_run_id)
        link = LinkValueObject(link)
        ggc = GroupGoogleCalendarEntity(ggc_id, course_run_id, name, link)
        try:
            await self.uow.ggc_repo.create(ggc)
            await self.uow.commit()
        except Exception:
            await self.uow.rollback()
            raise

    async def delete(self, group_google_calendar_id: str) -> None:
        group_google_calendar_id = UUID(group_google_calendar_id)
        try:
            await self.uow.ggc_repo.delete(group_google_calendar_id)
            await self.uow.commit()
        except Exception:
            await self.uow.rollback()
            raise

    async def get_groups(self, course_run_id: str) -> list[GroupGoogleCalendarEntity]:
        course_run_id = UUID(course_run_id)
        return await self.uow.ggc_repo.get_all_by_course_run_id(course_run_id)

    @staticmethod
    def __get_actual_course_run(course_runs:  list[CourseRunEntity], course_run_name: str) -> CourseRunEntity | None:
        for course_run in course_runs:
            if course_run.name.value == course_run_name:
                return course_run
        return None

    async def update(self, record: UpdateGroupGoogleCalendarDTO, course_run_name: str) -> str:
        updated_groups = set(record.groups)
        try:
            # Курс -> Актуальный запуск курса -> Текущие календари для групп этого запуска
            course_name = CourseName(record.course_name)
            course = await self.uow.course_repo.get_by_name(course_name)
            course_runs = await self.uow.course_run_repo.get_all_by_course_id(course.id)
            actual_course_run = self.__get_actual_course_run(course_runs, course_run_name)
            if not actual_course_run:
                return "Для курса нет запуска с указанным названием"
            ggc_list = await self.uow.ggc_repo.get_all_by_course_run_id(actual_course_run.id)
            current_groups: set[UpdateGroupDTO] = {UpdateGroupDTO(g.name, g.link.value) for g in ggc_list}
            # Добавляем новые группы
            to_add_groups: set[UpdateGroupDTO] = updated_groups - current_groups
            for g in to_add_groups:
                ggc_id = UUID(str(uuid.uuid4()))
                link = LinkValueObject(g.link)
                group = GroupGoogleCalendarEntity(ggc_id, actual_course_run.id, g.name, link)
                await self.uow.ggc_repo.create(group)
            # Удаляем старые группы
            to_remove_groups = current_groups - updated_groups
            for g in to_remove_groups:
                for current_group in ggc_list:
                    if current_group.link.value == g.link:
                        await self.uow.ggc_repo.delete(current_group.id)
            # Фиксируем изменения
            await self.uow.commit()
        except DomainError as e:
            await self.uow.rollback()
            return e.message
        except SQLAlchemyError as e:
            await self.uow.rollback()
            return str(e)
        else:
            return "OK"

===== END FILE =====

===== FILE: src/services/group_google_calendar/dto.py =====
from __future__ import annotations

from dataclasses import dataclass


@dataclass
class CreateGroupGoogleCalendarDTO:

    """DTO to create one group."""

    course_run_id: str
    name: str
    link: str


@dataclass(frozen=True)
class UpdateGroupDTO:

    """DTO to update one group."""

    name: str
    link: str


@dataclass
class UpdateGroupGoogleCalendarDTO:

    """DTO to update many groups."""

    course_name: str
    groups: list[UpdateGroupDTO]

===== END FILE =====

===== FILE: src/services/group_google_calendar/unit_of_work.py =====
from abc import ABC

from src.domain.course_run.course_run_repository import ICourseRunRepository
from src.domain.courses.course_repository import ICourseRepository
from src.domain.group_google_calendar.ggc_repository import IGroupGoogleCalendarRepository
from src.services.base_unit_of_work import ServiceUnitOfWork


class GroupGoogleCalendarUnitOfWork(ServiceUnitOfWork, ABC):

    """Base class implemented pattern Unit of Work."""

    ggc_repo: IGroupGoogleCalendarRepository
    course_repo: ICourseRepository
    course_run_repo: ICourseRunRepository

===== END FILE =====

===== FILE: src/services/playlists/__init__.py =====

===== END FILE =====

===== FILE: src/services/playlists/command_service.py =====
from __future__ import annotations

import datetime
import uuid
from typing import TYPE_CHECKING

from src.domain.base_value_objects import UUID, LinkValueObject
from src.domain.course_run.exceptions import NoActualCourseRunError
from src.domain.playlists.entities import PlaylistEntity
from src.domain.playlists.value_objects import VideoResourceType

if TYPE_CHECKING:
    from src.services.playlists.unit_of_work import PlaylistUnitOfWork


class PlaylistCommandService:

    """Class implemented CQRS pattern, command class."""

    def __init__(self, uow: PlaylistUnitOfWork) -> None:
        self.uow = uow

    async def get_playlists_by_course_run_id(self, course_run_id: str) -> list[PlaylistEntity]:
        course_run_id = UUID(course_run_id)
        return await self.uow.playlist_repo.get_all_by_course_run_id(course_run_id)

    async def get_actual_playlists(self, course_id: str) -> list[PlaylistEntity]:
        current_date = datetime.datetime.now().date()
        course_id = UUID(course_id)
        course_runs = await self.uow.course_run_repo.get_all_by_course_id(course_id)
        for course_run in course_runs:
            if course_run.is_actual_by_date(current_date):
                return await self.uow.playlist_repo.get_all_by_course_run_id(course_run.id)
        raise NoActualCourseRunError

    async def create_playlist(self, course_run_id: str, name: str, playlist_type: str, link: str) -> None:
        playlist_id = UUID(str(uuid.uuid4()))
        course_run_id = UUID(course_run_id)
        playlist_type = VideoResourceType(playlist_type)
        link = LinkValueObject(link)
        playlist = PlaylistEntity(playlist_id, course_run_id, name, playlist_type, link)
        try:
            await self.uow.playlist_repo.create(playlist)
            await self.uow.commit()
        except Exception:
            await self.uow.rollback()
            raise

    async def update_playlist(self, playlist_id: str, course_run_id: str, name: str, type_: str, link: str) -> None:
        playlist_id = UUID(playlist_id)
        course_run_id = UUID(course_run_id)
        playlist_type = VideoResourceType(type_)
        link = LinkValueObject(link)
        playlist = PlaylistEntity(playlist_id, course_run_id, name, playlist_type, link)
        try:
            await self.uow.playlist_repo.update(playlist)
            await self.uow.commit()
        except Exception:
            await self.uow.rollback()
            raise

    async def delete_playlist(self, playlist_id: str) -> None:
        playlist_id = UUID(playlist_id)
        try:
            await self.uow.playlist_repo.delete(playlist_id)
            await self.uow.commit()
        except Exception:
            await self.uow.rollback()
            raise

===== END FILE =====

===== FILE: src/services/playlists/unit_of_work.py =====
from abc import ABC

from src.domain.course_run.course_run_repository import ICourseRunRepository
from src.domain.playlists.playlist_repository import IPlaylistRepository
from src.services.base_unit_of_work import ServiceUnitOfWork


class PlaylistUnitOfWork(ServiceUnitOfWork, ABC):

    """Base class implemented pattern Unit of Work."""

    playlist_repo: IPlaylistRepository
    course_run_repo: ICourseRunRepository

===== END FILE =====

===== FILE: src/services/talent_profile/__init__.py =====

===== END FILE =====

===== FILE: src/services/talent_profile/command_service.py =====
from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy.exc import IntegrityError

from src.domain.auth.value_objects import PartOfName
from src.domain.base_value_objects import UUID, EmptyLinkValueObject
from src.domain.talent_profile.entities import TalentProfileEntity
from src.domain.talent_profile.exceptions import TalentProfileAlreadyExistsError, TalentProfileForOnlyTalentError

if TYPE_CHECKING:
    from src.services.talent_profile.unit_of_work import TalentProfileUnitOfWork


class TalentProfileCommandService:

    """Class implemented CQRS pattern, command class."""

    def __init__(self, uow: TalentProfileUnitOfWork) -> None:
        self.uow = uow

    async def create_profile(self, user_id: str, role: str) -> None:
        if role != "talent":
            raise TalentProfileForOnlyTalentError
        user_id = UUID(str(user_id))
        try:
            profile = TalentProfileEntity(user_id)
            await self.uow.profile_repo.create(profile)
            await self.uow.commit()
        except IntegrityError as ex:
            await self.uow.rollback()
            raise TalentProfileAlreadyExistsError from ex
        except Exception:
            await self.uow.rollback()
            raise

    async def update_profile(
            self, user_id: str, firstname: str, lastname: str, image_url: str | None,
            location: str, position: str, company: str,
    ) -> None:
        user_id = UUID(str(user_id))
        try:
            user = await self.uow.user_repo.get_by_id(user_id)
            user.firstname = PartOfName(firstname)
            user.lastname = PartOfName(lastname)
            await self.uow.user_repo.update(user)
            profile = await self.uow.profile_repo.get_by_user_id(user_id)
            profile.update_profile(image_url, location, position, company)
            await self.uow.profile_repo.update(profile)
            await self.uow.commit()
        except Exception:
            await self.uow.rollback()
            raise

    async def update_links(
            self, user_id: str, link_ru_resume: str, link_eng_resume: str,
            link_tg_personal: str, link_linkedin: str,
    ) -> None:
        user_id = UUID(str(user_id))
        link_ru_resume = EmptyLinkValueObject(link_ru_resume)
        link_eng_resume = EmptyLinkValueObject(link_eng_resume)
        link_tg_personal = EmptyLinkValueObject(link_tg_personal)
        link_linkedin = EmptyLinkValueObject(link_linkedin)
        try:
            profile = await self.uow.profile_repo.get_by_user_id(user_id)
            profile.update_links(link_ru_resume, link_eng_resume, link_tg_personal, link_linkedin)
            await self.uow.profile_repo.update(profile)
            await self.uow.commit()
        except Exception:
            await self.uow.rollback()
            raise

    async def delete(self, user_id: str) -> None:
        user_id = UUID(user_id)
        try:
            await self.uow.profile_repo.delete(user_id)
            await self.uow.commit()
        except Exception:
            await self.uow.rollback()
            raise

    async def get_profile(self, user_id: str) -> TalentProfileEntity:
        """Get firstname, lastname and talent profile information.

        :param user_id:
        :return:
        """
        user_id = UUID(user_id)
        return await self.uow.profile_repo.get_by_user_id(user_id)

===== END FILE =====

===== FILE: src/services/talent_profile/unit_of_work.py =====
from abc import ABC

from src.domain.auth.user_repository import IUserRepository
from src.domain.talent_profile.profile_repository import ITalentProfileRepository
from src.services.base_unit_of_work import ServiceUnitOfWork


class TalentProfileUnitOfWork(ServiceUnitOfWork, ABC):

    """Base class implemented pattern Unit of Work."""

    user_repo: IUserRepository
    profile_repo: ITalentProfileRepository

===== END FILE =====

===== FILE: src/services/timetable/__init__.py =====

===== END FILE =====

===== FILE: src/services/timetable/command_service.py =====
from __future__ import annotations

import datetime
import uuid
from typing import TYPE_CHECKING

from src.domain.base_value_objects import UUID
from src.domain.timetable.entities import DayRuleEntity, TimetableEntity, WeekRuleEntity
from src.domain.timetable.value_objects import Weekday

if TYPE_CHECKING:
    from src.services.timetable.unit_of_work import TimetableUnitOfWork


class TimetableCommandService:

    """Class implemented CQRS pattern, command class."""

    def __init__(self, uow: TimetableUnitOfWork) -> None:
        self.uow = uow

    async def get_timetable_by_course_run_id(self, course_run_id: str) -> TimetableEntity:
        course_run_id = UUID(course_run_id)
        return await self.uow.timetable_repo.get_by_id(course_run_id)

    async def create_day_rule(
            self, course_run_id: str, start_time: datetime.time, end_time: datetime.time, date: datetime.date,
    ) -> str:
        rule_id = UUID(str(uuid.uuid4()))
        course_run_id = UUID(course_run_id)
        rule = DayRuleEntity(rule_id, course_run_id, start_time, end_time, date)
        try:
            await self.uow.timetable_repo.create_rule(rule)
            await self.uow.commit()
        except Exception:
            await self.uow.rollback()
            raise
        return rule_id.value

    async def create_week_rule(
            self, course_run_id: str, start_time: datetime.time, end_time: datetime.time,
            start_period_date: datetime.date, end_period_date: datetime.date, weekdays: list[str],
    ) -> str:
        rule_id = UUID(str(uuid.uuid4()))
        course_run_id = UUID(course_run_id)
        weekdays = [Weekday(wd) for wd in weekdays]
        rule = WeekRuleEntity(
            rule_id, course_run_id, start_time, end_time, start_period_date, end_period_date, weekdays,
        )
        try:
            await self.uow.timetable_repo.create_rule(rule)
            await self.uow.commit()
        except Exception:
            await self.uow.rollback()
            raise
        return rule_id.value

    async def update_day_rule(
            self, rule_id: str, course_run_id: str, start_time: datetime.time,
            end_time: datetime.time, date: datetime.date,
    ) -> None:
        rule_id = UUID(rule_id)
        course_run_id = UUID(course_run_id)
        rule = DayRuleEntity(rule_id, course_run_id, start_time, end_time, date)
        try:
            await self.uow.timetable_repo.update_rule(rule)
            await self.uow.commit()
        except Exception:
            await self.uow.rollback()
            raise

    async def update_week_rule(
            self, rule_id: str, course_run_id: str, start_time: datetime.time, end_time: datetime.time,
            start_period_date: datetime.date, end_period_date: datetime.date, weekdays: list[str],
    ) -> None:
        rule_id = UUID(rule_id)
        course_run_id = UUID(course_run_id)
        weekdays = [Weekday(wd) for wd in weekdays]
        rule = WeekRuleEntity(
            rule_id, course_run_id, start_time, end_time, start_period_date, end_period_date, weekdays,
        )
        try:
            await self.uow.timetable_repo.update_rule(rule)
            await self.uow.commit()
        except Exception:
            await self.uow.rollback()
            raise

    async def delete_rule(self, rule_id: str) -> None:
        rule_id = UUID(rule_id)
        try:
            await self.uow.timetable_repo.delete_rule(rule_id)
            await self.uow.commit()
        except Exception:
            await self.uow.rollback()
            raise

===== END FILE =====

===== FILE: src/services/timetable/unit_of_work.py =====
from abc import ABC

from src.domain.timetable.timetable_repository import ITimetableRepository
from src.services.base_unit_of_work import ServiceUnitOfWork


class TimetableUnitOfWork(ServiceUnitOfWork, ABC):

    """Base class implemented pattern Unit of Work."""

    timetable_repo: ITimetableRepository

===== END FILE =====

===== FILE: unit_tests/__init__.py =====

===== END FILE =====

===== FILE: unit_tests/domain/__init__.py =====

===== END FILE =====

===== FILE: unit_tests/domain/auth/__init__.py =====

===== END FILE =====

===== FILE: unit_tests/domain/auth/test_entity.py =====
import uuid

from src.domain.auth.entities import UserEntity
from src.domain.auth.value_objects import PartOfName, UserRole, Email
from src.domain.base_value_objects import UUID


def test_correct_user():
    user = UserEntity(
        id=UUID(str(uuid.uuid4())),
        firstname=PartOfName("Nick"),
        lastname=PartOfName("Cargo"),
        role=UserRole("admin"),
        email=Email("nick@cargo.com"),
        hashed_password="32rserfs4t4ts4t4"
    )
    assert user.role == UserRole("admin")
    assert user.firstname == PartOfName("Nick")
    assert user.lastname == PartOfName("Cargo")
    assert user.email == Email("nick@cargo.com")
    assert user.hashed_password == "32rserfs4t4ts4t4"

===== END FILE =====

===== FILE: unit_tests/domain/auth/test_value_objects.py =====
import pytest

from src.domain.auth.exceptions import EmailNotValidError, RoleDoesntExistError, EmptyPartOfNameError
from src.domain.auth.value_objects import Email, USER_ROLES, UserRole, PartOfName


def test_correct_email():
    email_string = "john@gmail.com"
    email = Email(email_string)
    assert email.value == email_string


@pytest.mark.parametrize("email_string", [
    "gmail.com", "johny", "joe@", "@joe", "@@@"
])
def test_incorrect_email(email_string):
    with pytest.raises(EmailNotValidError):
        Email(email_string)


def test_correct_role():
    role_string = USER_ROLES[0]
    role = UserRole(role_string)
    assert role.value == role_string


def test_incorrect_role():
    role_string = "another"
    with pytest.raises(RoleDoesntExistError):
        UserRole(role_string)


def test_correct_part_of_name():
    part_of_name_string = "Johny"
    role = PartOfName(part_of_name_string)
    assert role.value == part_of_name_string


def test_incorrect_part_of_name():
    part_of_name_string = ""
    with pytest.raises(EmptyPartOfNameError):
        PartOfName(part_of_name_string)
===== END FILE =====

===== FILE: unit_tests/domain/course_run/__init__.py =====

===== END FILE =====

===== FILE: unit_tests/domain/course_run/test_entity.py =====
import uuid

import pytest

from src.domain.base_value_objects import UUID
from src.domain.course_run.entities import CourseRunEntity
from src.domain.courses.exceptions import IncorrectCourseRunNameError
from src.domain.courses.value_objects import CourseRun


def test_correct_course_run():
    course_run = CourseRunEntity(
        id=UUID(str(uuid.uuid4())),
        name=CourseRun("Весна 2025"),
        course_id=UUID(str(uuid.uuid4()))
    )
    assert course_run.name.value == "Весна 2025"


@pytest.mark.parametrize("name", [
    "Зима 2024",
    "Весна",
    "2024",
    "2024 Весна"
])
def test_incorrect_course_run(name):
    with pytest.raises(IncorrectCourseRunNameError):
        CourseRunEntity(
            id=UUID(str(uuid.uuid4())),
            name=CourseRun(name),
            course_id=UUID(str(uuid.uuid4()))
        )

===== END FILE =====

===== FILE: unit_tests/domain/courses/__init__.py =====

===== END FILE =====

===== FILE: unit_tests/domain/courses/test_entity.py =====
import uuid

import pytest

from src.domain.base_value_objects import UUID
from src.domain.courses.entities import CourseEntity
from src.domain.courses.exceptions import CoursePublishError
from src.domain.courses.constants import IMPLEMENTERS, ROLES, FORMATS, PERIODS, TERMS
from src.domain.courses.value_objects import CourseName, Author, Implementer, Format, Terms, Role, CourseRun, Period


def test_correct_course():
    course_id = UUID(str(uuid.uuid4()))
    course = CourseEntity(
        id=course_id,
        name=CourseName("Java"),
    )
    assert course.id == course_id
    assert course.name == CourseName("Java")
    assert course.image_url is None
    assert len(course.roles) != []


def test_publish_empty_course():
    course = CourseEntity(
        id=UUID(str(uuid.uuid4())),
        name=CourseName("Java"),
    )
    with pytest.raises(CoursePublishError):
        course.publish()


def test_publish_already_published_course():
    course = CourseEntity(
        id=UUID(str(uuid.uuid4())),
        name=CourseName("Java"),
        is_draft=False
    )
    with pytest.raises(CoursePublishError):
        course.publish()


def test_publish_full_course():
    course = CourseEntity(
        id=UUID(str(uuid.uuid4())),
        name=CourseName("Java"),
        image_url="path-to-logo.jpg",
        author=Author("Иванов И. И."),
        implementer=Implementer(IMPLEMENTERS[0]),
        format=Format(FORMATS[0]),
        terms=Terms(TERMS[0]),
        roles=[Role(ROLES[0])],
        periods=[Period(PERIODS[0])],
        last_runs=[CourseRun("Весна 2023")],
    )
    course.publish()
    assert not course.is_draft


def test_hide_draft_course():
    course = CourseEntity(
        id=UUID(str(uuid.uuid4())),
        name=CourseName("Java"),
        image_url="path-to-logo.jpg",
        author=Author("Иванов И. И."),
        implementer=Implementer(IMPLEMENTERS[0]),
        format=Format(FORMATS[0]),
        terms=Terms(TERMS[0]),
        roles=[Role(ROLES[0])],
        periods=[Period(PERIODS[0])],
    )
    with pytest.raises(CoursePublishError):
        course.hide()


def test_hide_published_course():
    course = CourseEntity(
        id=UUID(str(uuid.uuid4())),
        name=CourseName("Java"),
        is_draft=False
    )
    course.hide()
    assert course.is_draft

===== END FILE =====

===== FILE: unit_tests/domain/courses/test_value_objects.py =====
import pytest

from src.domain.courses.exceptions import EmptyPropertyError, ValueDoesntExistError, IncorrectCourseRunNameError
from src.domain.courses.value_objects import CourseName, Author, Implementer, Format, CourseRun
from src.domain.courses.constants import IMPLEMENTERS, FORMATS


def test_correct_course_name():
    course_name_string = "Python"
    course_name = CourseName(course_name_string)
    assert course_name.value == course_name_string


def test_incorrect_course_name():
    with pytest.raises(EmptyPropertyError):
        CourseName("")


def test_correct_author():
    author_string = "Иванов И.И., ктн"
    author = Author(author_string)
    assert author.value == author_string


def test_incorrect_author():
    with pytest.raises(EmptyPropertyError):
        Author("")


def test_correct_implementer():
    implementer_string = IMPLEMENTERS[0]
    implementer = Implementer(implementer_string)
    assert implementer.value == implementer_string


def test_incorrect_implementer():
    with pytest.raises(ValueDoesntExistError):
        Implementer("Неизвестный реализатор")


def test_correct_format():
    format_string = FORMATS[0]
    format_ = Format(format_string)
    assert format_.value == format_string


def test_incorrect_format():
    with pytest.raises(ValueDoesntExistError):
        Format("Неизвестный формат")


def test_correct_run():
    run_string = "Весна 2023"
    run = CourseRun(run_string)
    assert run.value == run_string


@pytest.mark.parametrize("run_name", [
    "", "Весна", "Весна 1992", "Весна 2992", "Зима 2023", "2034",
])
def test_incorrect_run(run_name):
    with pytest.raises(IncorrectCourseRunNameError):
        CourseRun(run_name)

===== END FILE =====

===== FILE: unit_tests/domain/feedback/__init__.py =====

===== END FILE =====

===== FILE: unit_tests/domain/feedback/test_entity.py =====
import datetime
import uuid

import pytest

from src.domain.base_value_objects import UUID
from src.domain.feedback.entities import FeedbackEntity
from src.domain.feedback.exceptions import FeedbackLikeError
from src.domain.feedback.value_objects import FeedbackText, Vote, Rating


@pytest.fixture
def correct_feedback() -> FeedbackEntity:
    feedback_id = UUID(str(uuid.uuid4()))
    course_id = UUID(str(uuid.uuid4()))
    author_id = UUID(str(uuid.uuid4()))
    text = FeedbackText("Cool!")
    rating = Rating(5)
    date = datetime.date(year=2024, month=12, day=1)
    return FeedbackEntity(feedback_id, course_id, author_id, text, rating, set(), date)


def test_correct_feedback(correct_feedback):
    assert correct_feedback.text == FeedbackText("Cool!")
    assert correct_feedback.date == datetime.date(year=2024, month=12, day=1)


def test_no_votes(correct_feedback):
    assert correct_feedback.reputation == 0
    assert len(correct_feedback.votes) == 0


def test_add_votes(correct_feedback):
    user_id, vote_type = UUID(str(uuid.uuid4())), "like"
    correct_feedback.vote(user_id, vote_type)
    assert correct_feedback.reputation == 1
    assert len(correct_feedback.votes) == 1
    alternative_vote_type = "dislike"
    correct_feedback.vote(user_id, alternative_vote_type)
    assert correct_feedback.reputation == -1
    assert len(correct_feedback.votes) == 1


def test_add_votes_many_users(correct_feedback):
    user_1_id, vote_1_type = UUID(str(uuid.uuid4())), "like"
    user_2_id, vote_2_type = UUID(str(uuid.uuid4())), "dislike"
    correct_feedback.vote(user_1_id, vote_1_type)
    correct_feedback.vote(user_2_id, vote_2_type)
    assert correct_feedback.reputation == 0
    assert len(correct_feedback.votes) == 2


def test_add_same_vote_from_one_user(correct_feedback):
    user_id, vote_type = UUID(str(uuid.uuid4())), "like"
    correct_feedback.vote(user_id, vote_type)
    with pytest.raises(FeedbackLikeError):
        correct_feedback.vote(user_id, vote_type)


def test_add_vote_from_author(correct_feedback):
    with pytest.raises(FeedbackLikeError):
        correct_feedback.vote(correct_feedback.author_id, "like")


def test_unvote(correct_feedback):
    user_id, vote_type = UUID(str(uuid.uuid4())), "like"
    correct_feedback.unvote(user_id)
    correct_feedback.vote(user_id, vote_type)
    correct_feedback.unvote(user_id)

===== END FILE =====

===== FILE: unit_tests/domain/feedback/test_value_objects.py =====
import uuid

import pytest

from src.domain.base_value_objects import UUID
from src.domain.courses.exceptions import EmptyPropertyError, ValueDoesntExistError
from src.domain.feedback.value_objects import FeedbackText, Vote, Rating


def test_correct_feedback_text():
    feedback_text_string = "Good course!"
    feedback_text = FeedbackText(feedback_text_string)
    assert feedback_text.value == feedback_text_string


def test_incorrect_feedback_text():
    with pytest.raises(EmptyPropertyError):
        FeedbackText("")


def test_correct_feedback_rating():
    feedback_rating_number = 1
    feedback_rating = Rating(feedback_rating_number)
    assert feedback_rating.value == feedback_rating_number


def test_incorrect_feedback_rating():
    with pytest.raises(ValueDoesntExistError):
        Rating(-1)


def test_correct_vote():
    user_id = UUID(str(uuid.uuid4()))
    vote_type_string = "like"
    vote = Vote(user_id, vote_type_string)
    assert vote.vote_type == vote_type_string
    assert vote.user_id == user_id


def test_incorrect_vote():
    with pytest.raises(ValueDoesntExistError):
        Vote(UUID(str(uuid.uuid4())), "unlike")

===== END FILE =====

===== FILE: unit_tests/domain/talent_profile/__init__.py =====

===== END FILE =====

===== FILE: unit_tests/domain/talent_profile/test_value_objects.py =====
import pytest

from src.domain.base_exceptions import InvalidLinkError
from src.domain.base_value_objects import LinkValueObject, EmptyLinkValueObject


def test_correct_link():
    link_string = "https://www.tele-gram.ai"
    link = LinkValueObject(value=link_string)
    assert link.value == link_string


def test_incorrect_link():
    with pytest.raises(InvalidLinkError):
        LinkValueObject(value="www.tele")


def test_correct_empty_link():
    link_string = ""
    link = EmptyLinkValueObject(value=link_string)
    assert link.value == link_string

===== END FILE =====

===== FILE: unit_tests/domain/timetable/__init__.py =====

===== END FILE =====

===== FILE: unit_tests/domain/timetable/test_entity.py =====
import datetime
import uuid

from src.domain.base_value_objects import UUID
from src.domain.timetable.entities import DayRuleEntity, WeekRuleEntity, TimetableEntity
from src.domain.timetable.value_objects import Weekday


def test_day_rule_lessons():
    year, month, day = 2024, 12, 1
    h1, m1 = 17, 0
    h2, m2 = 18, 30
    rule = DayRuleEntity(
        id=UUID(str(uuid.uuid4())),
        timetable_id=UUID(str(uuid.uuid4())),
        start_time=datetime.time(h1, m1),
        end_time=datetime.time(h2, m2),
        date=datetime.date(year, month, day),
    )
    rule_lessons = rule.lessons
    assert len(rule_lessons) == 1
    assert rule_lessons[0].start_time == datetime.datetime(year, month, day, h1, m1)
    assert rule_lessons[0].end_time == datetime.datetime(year, month, day, h2, m2)


def test_week_rule_lessons_no_weekdays():
    year, month, d1, d2 = 2024, 12, 1, 10
    h1, m1, s = 17, 0, 0
    h2, m2, s = 18, 30, 0
    rule = WeekRuleEntity(
        id=UUID(str(uuid.uuid4())),
        timetable_id=UUID(str(uuid.uuid4())),
        start_time=datetime.time(h1, m1, s),
        end_time=datetime.time(h2, m2, s),
        start_period_date=datetime.date(year, month, d1),
        end_period_date=datetime.date(year, month, d2),
        weekdays=[]
    )
    rule_lessons = rule.lessons
    assert len(rule_lessons) == 0


def test_week_rule_lessons_one_weekday():
    year, month, d1, d2 = 2024, 12, 1, 10
    h1, m1, s = 17, 0, 0
    h2, m2, s = 18, 30, 0
    rule = WeekRuleEntity(
        id=UUID(str(uuid.uuid4())),
        timetable_id=UUID(str(uuid.uuid4())),
        start_time=datetime.time(h1, m1, s),
        end_time=datetime.time(h2, m2, s),
        start_period_date=datetime.date(year, month, d1),
        end_period_date=datetime.date(year, month, d2),
        weekdays=[Weekday("пн")]
    )
    rule_lessons = rule.lessons
    assert len(rule_lessons) == 2
    assert rule_lessons[0].start_time == datetime.datetime(2024, 12, 2, h1, m1, s)
    assert rule_lessons[0].end_time == datetime.datetime(2024, 12, 2, h2, m2, s)
    assert rule_lessons[1].start_time == datetime.datetime(2024, 12, 9, h1, m1, s)
    assert rule_lessons[1].end_time == datetime.datetime(2024, 12, 9, h2, m2, s)


def test_week_rule_lessons_two_weekdays():
    year, month, d1, d2 = 2024, 12, 1, 10
    h1, m1, s = 17, 0, 0
    h2, m2, s = 18, 30, 0
    rule = WeekRuleEntity(
        id=UUID(str(uuid.uuid4())),
        timetable_id=UUID(str(uuid.uuid4())),
        start_time=datetime.time(h1, m1, s),
        end_time=datetime.time(h2, m2, s),
        start_period_date=datetime.date(year, month, d1),
        end_period_date=datetime.date(year, month, d2),
        weekdays=[Weekday("пн"), Weekday("ср")]
    )
    rule_lessons = rule.lessons
    assert len(rule_lessons) == 3
    assert rule_lessons[0].start_time.time() == datetime.time(h1, m1, s)
    assert rule_lessons[0].end_time.time() == datetime.time(h2, m2, s)


def test_timetable_no_warnings():
    year, month, day = 2024, 12, 1
    h1, m1 = 17, 0
    h2, m2 = 18, 30
    rule = DayRuleEntity(
        id=UUID(str(uuid.uuid4())),
        timetable_id=UUID(str(uuid.uuid4())),
        start_time=datetime.time(h1, m1),
        end_time=datetime.time(h2, m2),
        date=datetime.date(year, month, day),
    )
    timetable = TimetableEntity(
        id=UUID(str(uuid.uuid4())),
        course_run_id=UUID(str(uuid.uuid4())),
        rules=[rule]
    )
    assert len(timetable.rules) == 1
    assert len(timetable.lessons) == 1
    assert len(timetable.warnings) == 0


def test_timetable_with_warnings():
    year, month, day = 2024, 12, 1
    h1, m1 = 17, 0
    h2, m2 = 18, 30
    rule = DayRuleEntity(
        id=UUID(str(uuid.uuid4())),
        timetable_id=UUID(str(uuid.uuid4())),
        start_time=datetime.time(h1, m1),
        end_time=datetime.time(h2, m2),
        date=datetime.date(year, month, day),
    )
    timetable = TimetableEntity(
        id=UUID(str(uuid.uuid4())),
        course_run_id=UUID(str(uuid.uuid4())),
        rules=[rule, rule]
    )
    assert len(timetable.rules) == 2
    assert len(timetable.lessons) == 2
    assert len(timetable.warnings) == 1

===== END FILE =====