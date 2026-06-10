"""Create cache table

Revision ID: 002
Revises: 001
Create Date: 2026-01-26

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "002"
down_revision: Union[str, None] = "001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create cache table for storing generated report references."""
    op.create_table(
        "report_cache",
        # Primary key - composite of report + params hash
        sa.Column("cache_key", sa.String(100), primary_key=True),

        # Report information
        sa.Column("report_id", sa.String(50), nullable=False, index=True),
        sa.Column("parameters_hash", sa.String(64), nullable=False),  # SHA256 hash
        sa.Column("parameters", postgresql.JSONB, nullable=False, default={}),

        # Result location
        sa.Column("gcs_path", sa.String(500), nullable=False),

        # Cache timing
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False, index=True),

        # Metadata
        sa.Column("size_bytes", sa.BigInteger, nullable=True),
        sa.Column("hit_count", sa.Integer, nullable=False, default=0),
        sa.Column("last_hit_at", sa.DateTime(timezone=True), nullable=True),
    )

    # Index for expiration cleanup
    op.create_index(
        "ix_report_cache_expires_at",
        "report_cache",
        ["expires_at"],
    )

    # Index for report-specific queries
    op.create_index(
        "ix_report_cache_report_id_params",
        "report_cache",
        ["report_id", "parameters_hash"],
    )


def downgrade() -> None:
    """Drop cache table."""
    op.drop_index("ix_report_cache_report_id_params", table_name="report_cache")
    op.drop_index("ix_report_cache_expires_at", table_name="report_cache")
    op.drop_table("report_cache")
