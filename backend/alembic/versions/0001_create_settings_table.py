"""create settings table

Revision ID: 0001
Revises:
Create Date: 2026-07-20

The first table in the app — a generic key/value store for the settings
domain (see docs/architecture/03_DATABASE_DESIGN.md and
docs/features/008_Settings.md). Deliberately schema-less per-setting: a new
setting is a new row, not a new column or a new migration.
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "0001"
down_revision: str | None = None
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "settings",
        sa.Column("key", sa.String(length=64), primary_key=True),
        sa.Column("value", sa.Text(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("settings")
