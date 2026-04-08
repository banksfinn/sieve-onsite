"""replace clip_feedback delivery_id with dataset_id and dataset_version_id

Revision ID: a1b2c3d4e5f6
Revises: 587a86d28f28
Create Date: 2026-04-08 21:31:37.000000+00:00

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "a1b2c3d4e5f6"
down_revision: Union[str, None] = "587a86d28f28"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("clip_feedback", sa.Column("dataset_id", sa.Integer(), nullable=True))
    op.add_column("clip_feedback", sa.Column("dataset_version_id", sa.Integer(), nullable=True))

    # Backfill from the clip's dataset_version_id and the version's dataset_id
    op.execute("""
        UPDATE clip_feedback cf
        SET dataset_version_id = c.dataset_version_id,
            dataset_id = dv.dataset_id
        FROM clips c
        JOIN dataset_versions dv ON dv.id = c.dataset_version_id
        WHERE cf.clip_id = c.id
    """)

    op.alter_column("clip_feedback", "dataset_id", nullable=False)
    op.alter_column("clip_feedback", "dataset_version_id", nullable=False)

    op.create_foreign_key("fk_clip_feedback_dataset_id", "clip_feedback", "datasets", ["dataset_id"], ["id"])
    op.create_foreign_key("fk_clip_feedback_dataset_version_id", "clip_feedback", "dataset_versions", ["dataset_version_id"], ["id"])

    op.drop_constraint("clip_feedback_delivery_id_fkey", "clip_feedback", type_="foreignkey")
    op.drop_column("clip_feedback", "delivery_id")


def downgrade() -> None:
    op.add_column("clip_feedback", sa.Column("delivery_id", sa.Integer(), nullable=True))
    op.create_foreign_key("clip_feedback_delivery_id_fkey", "clip_feedback", "deliveries", ["delivery_id"], ["id"])

    op.drop_constraint("fk_clip_feedback_dataset_version_id", "clip_feedback", type_="foreignkey")
    op.drop_constraint("fk_clip_feedback_dataset_id", "clip_feedback", type_="foreignkey")
    op.drop_column("clip_feedback", "dataset_version_id")
    op.drop_column("clip_feedback", "dataset_id")
