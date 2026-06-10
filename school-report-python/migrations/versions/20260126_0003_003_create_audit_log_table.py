"""Create audit log table

Revision ID: 003
Revises: 002
Create Date: 2026-01-26

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "003"
down_revision: Union[str, None] = "002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create audit log table for tracking all report generation events."""
    op.create_table(
        "audit_logs",
        # Primary key
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),

        # Job reference
        sa.Column(
            "job_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("jobs.id", ondelete="SET NULL"),
            nullable=True,
            index=True,
        ),

        # Report information
        sa.Column("report_id", sa.String(50), nullable=False, index=True),
        sa.Column("parameters", postgresql.JSONB, nullable=False, default={}),

        # Requester information
        sa.Column("requester", sa.String(255), nullable=True, index=True),
        sa.Column("requester_ip", sa.String(45), nullable=True),
        sa.Column("user_agent", sa.String(500), nullable=True),

        # Status tracking
        sa.Column(
            "status",
            sa.String(20),
            nullable=False,
            index=True,
        ),
        # Status values: processing, completed, failed

        # Timing
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("duration_ms", sa.Integer, nullable=True),

        # Result
        sa.Column("gcs_path", sa.String(500), nullable=True),
        sa.Column("error", sa.Text, nullable=True),
        sa.Column("cached", sa.Boolean, nullable=False, default=False),

        # Extra metadata
        sa.Column("metadata", postgresql.JSONB, nullable=True),

        # Record timestamp
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )

    # Index for time-based queries
    op.create_index(
        "ix_audit_logs_created_at",
        "audit_logs",
        ["created_at"],
    )

    # Composite index for filtering
    op.create_index(
        "ix_audit_logs_report_status",
        "audit_logs",
        ["report_id", "status"],
    )

    op.create_index(
        "ix_audit_logs_requester_created",
        "audit_logs",
        ["requester", "created_at"],
    )


def downgrade() -> None:
    """Drop audit log table."""
    op.drop_index("ix_audit_logs_requester_created", table_name="audit_logs")
    op.drop_index("ix_audit_logs_report_status", table_name="audit_logs")
    op.drop_index("ix_audit_logs_created_at", table_name="audit_logs")
    op.drop_table("audit_logs")
