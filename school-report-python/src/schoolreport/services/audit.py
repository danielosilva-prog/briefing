"""Audit logging service."""

import logging
from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from schoolreport.core.postgres import PostgresClient

logger = logging.getLogger(__name__)


class AuditService:
    """
    Audit logging service for tracking report generation.

    Records who requested what report when, with full event trail.
    """

    def __init__(self, postgres_client: PostgresClient):
        """
        Initialize audit service.

        Args:
            postgres_client: PostgreSQL client
        """
        self.postgres = postgres_client

    async def log_start(
        self,
        job_id: UUID,
        report_id: str,
        parameters: dict,
        requester: str,
        metadata: Optional[dict] = None
    ) -> UUID:
        """
        Log the start of a report generation job.

        Args:
            job_id: Job identifier
            report_id: Report type
            parameters: Report parameters
            requester: User/service requesting
            metadata: Optional extra metadata

        Returns:
            Audit log ID
        """
        audit_id = uuid4()

        try:
            await self.postgres.execute(
                """
                INSERT INTO audit_logs (
                    id, job_id, report_id, parameters, requester,
                    status, started_at, metadata, created_at
                )
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
                """,
                {
                    "id": audit_id,
                    "job_id": job_id,
                    "report_id": report_id,
                    "parameters": parameters,
                    "requester": requester,
                    "status": "processing",
                    "started_at": datetime.utcnow(),
                    "metadata": metadata or {},
                    "created_at": datetime.utcnow()
                }
            )

            logger.info(f"Audit log created: {audit_id} for job {job_id}")
            return audit_id

        except Exception as e:
            logger.error(f"Failed to create audit log: {e}")
            raise

    async def log_complete(
        self,
        audit_id: UUID,
        gcs_path: str,
        duration_ms: int
    ) -> None:
        """
        Log successful completion.

        Args:
            audit_id: Audit log ID
            gcs_path: Output file location
            duration_ms: Processing duration
        """
        try:
            await self.postgres.execute(
                """
                UPDATE audit_logs
                SET status = $1,
                    completed_at = $2,
                    duration_ms = $3,
                    gcs_path = $4
                WHERE id = $5
                """,
                {
                    "status": "completed",
                    "completed_at": datetime.utcnow(),
                    "duration_ms": duration_ms,
                    "gcs_path": gcs_path,
                    "id": audit_id
                }
            )

            logger.info(f"Audit log completed: {audit_id}")

        except Exception as e:
            logger.error(f"Failed to update audit log: {e}")

    async def log_failure(
        self,
        audit_id: UUID,
        error: str,
        duration_ms: int
    ) -> None:
        """
        Log failure.

        Args:
            audit_id: Audit log ID
            error: Error message
            duration_ms: Processing duration before failure
        """
        try:
            await self.postgres.execute(
                """
                UPDATE audit_logs
                SET status = $1,
                    completed_at = $2,
                    duration_ms = $3,
                    error = $4
                WHERE id = $5
                """,
                {
                    "status": "failed",
                    "completed_at": datetime.utcnow(),
                    "duration_ms": duration_ms,
                    "error": error,
                    "id": audit_id
                }
            )

            logger.info(f"Audit log failed: {audit_id}")

        except Exception as e:
            logger.error(f"Failed to update audit log: {e}")

    async def query(
        self,
        report_id: Optional[str] = None,
        requester: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 100
    ) -> list[dict]:
        """
        Query audit logs.

        Args:
            report_id: Filter by report ID
            requester: Filter by requester
            status: Filter by status
            limit: Max results

        Returns:
            List of audit log entries
        """
        where_clauses = []
        params = {}

        if report_id:
            where_clauses.append("report_id = $report_id")
            params["report_id"] = report_id

        if requester:
            where_clauses.append("requester = $requester")
            params["requester"] = requester

        if status:
            where_clauses.append("status = $status")
            params["status"] = status

        where_sql = f"WHERE {' AND '.join(where_clauses)}" if where_clauses else ""

        sql = f"""
            SELECT *
            FROM audit_logs
            {where_sql}
            ORDER BY created_at DESC
            LIMIT $limit
        """
        params["limit"] = limit

        try:
            rows = await self.postgres.fetch(sql, params)
            return rows or []

        except Exception as e:
            logger.error(f"Audit query failed: {e}")
            return []
