"""add recurrence fields to todos

Revision ID: 8005c70fed50
Revises: a2a08da44ea2
Create Date: 2025-12-29 21:05:56.883278+00:00

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "8005c70fed50"
down_revision: Union[str, None] = "a2a08da44ea2"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("todos", sa.Column("recurrence_rule", sa.String(), nullable=True))
    op.add_column("todos", sa.Column("recurrence_start", sa.DateTime(timezone=True), nullable=True))
    op.add_column("todos", sa.Column("recurrence_end", sa.DateTime(timezone=True), nullable=True))
    op.add_column("todos", sa.Column("recurrence_type", sa.String(), nullable=True))


def downgrade() -> None:
    op.drop_column("todos", "recurrence_type")
    op.drop_column("todos", "recurrence_end")
    op.drop_column("todos", "recurrence_start")
    op.drop_column("todos", "recurrence_rule")
