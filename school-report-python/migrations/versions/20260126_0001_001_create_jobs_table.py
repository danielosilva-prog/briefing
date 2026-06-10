"""Create jobs table

Revision ID: 001
Revises: None
Create Date: 2026-01-26

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create jobs table for tracking report generation jobs."""
    op.create_table(
        "jobs",
        # Primary key
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),

        # Report information
        sa.Column("report_id", sa.String(50), nullable=False, index=True),
        sa.Column("parameters", postgresql.JSONB, nullable=False, default={}),

        # Job status
        sa.Column(
            "status",
            sa.String(20),
            nullable=False,
            default="queued",
            index=True,
        ),
        # Status values: queued, processing, completed, failed, cancelled

        # Requester information
        sa.Column("requester", sa.String(255), nullable=True),
        sa.Column("requester_ip", sa.String(45), nullable=True),  # IPv6 max length

        # Result information
        sa.Column("gcs_path", sa.String(500), nullable=True),
        sa.Column("error", sa.Text, nullable=True),
        sa.Column("cached", sa.Boolean, nullable=False, default=False),

        # Timing
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("duration_ms", sa.Integer, nullable=True),

        # Retry tracking
        sa.Column("attempts", sa.Integer, nullable=False, default=0),
        sa.Column("max_attempts", sa.Integer, nullable=False, default=3),

        # Metadata
        sa.Column("metadata", postgresql.JSONB, nullable=True),
    )

    # Create indexes for common queries
    op.create_index(
        "ix_jobs_status_created_at",
        "jobs",
        ["status", "created_at"],
    )

    op.create_index(
        "ix_jobs_report_id_created_at",
        "jobs",
        ["report_id", "created_at"],
    )

    op.create_index(
        "ix_jobs_requester",
        "jobs",
        ["requester"],
    )


def downgrade() -> None:
    """Drop jobs table."""
    op.drop_index("ix_jobs_requester", table_name="jobs")
    op.drop_index("ix_jobs_report_id_created_at", table_name="jobs")
    op.drop_index("ix_jobs_status_created_at", table_name="jobs")
    op.drop_table("jobs")
