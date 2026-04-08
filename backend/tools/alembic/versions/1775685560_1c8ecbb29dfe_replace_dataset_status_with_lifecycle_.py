"""replace dataset status with lifecycle and request_status columns

Revision ID: 1c8ecbb29dfe
Revises: f6afff5c9c03
Create Date: 2026-04-08 21:59:20.253267+00:00

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "1c8ecbb29dfe"
down_revision: Union[str, None] = "f6afff5c9c03"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add new columns with defaults so existing rows get values
    op.add_column(
        "datasets",
        sa.Column("lifecycle", sa.String(), nullable=False, server_default="pending"),
    )
    op.add_column(
        "datasets",
        sa.Column("request_status", sa.String(), nullable=False, server_default="requested"),
    )

    # Migrate existing data from status to the new columns
    # requested -> lifecycle=pending, request_status=requested (defaults, no-op)
    # initialized -> lifecycle=active, request_status=in_progress
    # active -> lifecycle=active, request_status=in_progress
    op.execute(
        """
        UPDATE datasets
        SET lifecycle = 'active', request_status = 'in_progress'
        WHERE status IN ('initialized', 'active')
        """
    )

    # Drop old column and server defaults
    op.drop_column("datasets", "status")
    op.alter_column("datasets", "lifecycle", server_default=None)
    op.alter_column("datasets", "request_status", server_default=None)


def downgrade() -> None:
    op.add_column(
        "datasets",
        sa.Column(
            "status",
            sa.VARCHAR(),
            server_default=sa.text("'requested'::character varying"),
            autoincrement=False,
            nullable=False,
        ),
    )

    # Map back: pending -> requested, active -> active
    op.execute(
        """
        UPDATE datasets
        SET status = CASE
            WHEN lifecycle = 'pending' THEN 'requested'
            WHEN lifecycle = 'active' THEN 'active'
            ELSE 'requested'
        END
        """
    )

    op.drop_column("datasets", "request_status")
    op.drop_column("datasets", "lifecycle")
