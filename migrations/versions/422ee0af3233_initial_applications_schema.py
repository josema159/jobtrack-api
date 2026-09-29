"""Initial applications schema

Revision ID: 422ee0af3233
Revises: 
Create Date: 2026-09-29 18:08:47.202176

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '422ee0af3233'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "applications",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("company", sa.String(length=100), nullable=False),
        sa.Column("position", sa.String(length=100), nullable=False),
        sa.Column("country", sa.String(length=100), nullable=True),
        sa.Column("status", sa.String(length=30), nullable=False),
        sa.Column("job_url", sa.String(length=500), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint("id")
    )

    op.create_index(
        op.f("ix_applications_id"),
        "applications",
        ["id"],
        unique=False
    )

def downgrade() -> None:
    op.drop_index(
        op.f("ix_applications_id"),
        table_name="applications"
    )

    op.drop_table("applications")