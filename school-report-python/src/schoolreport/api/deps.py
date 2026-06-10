"""Dependency injection for FastAPI routes."""

import logging
from typing import AsyncGenerator

from google.cloud import bigquery
from redis.asyncio import Redis, ConnectionPool
import asyncpg
from arq import create_pool
from arq.connections import RedisSettings, ArqRedis

from schoolreport.config import Settings, get_settings as _get_settings

logger = logging.getLogger(__name__)

# Global connection pools (initialized once)
_redis_pool: ConnectionPool | None = None
_postgres_pool: asyncpg.Pool | None = None
_bigquery_client: bigquery.Client | None = None


def get_settings() -> Settings:
    """
    Get application settings.

    Returns:
        Settings: Application configuration

    Example:
        ```python
        @app.get("/example")
        async def example_route(settings: Settings = Depends(get_settings)):
            return {"project": settings.gcp_project_id}
        ```
    """
    return _get_settings()


async def get_redis() -> AsyncGenerator[Redis, None]:
    """
    Get Redis client from connection pool.

    Yields:
        Redis: Redis async client

    Example:
        ```python
        @app.get("/example")
        async def example_route(redis: Redis = Depends(get_redis)):
            await redis.set("key", "value")
            return {"status": "ok"}
        ```
    """
    global _redis_pool

    settings = get_settings()

    # Initialize pool on first use
    if _redis_pool is None:
        logger.info(f"Initializing Redis connection pool: {settings.redis_url}")
        _redis_pool = ConnectionPool.from_url(
            str(settings.redis_url),
            decode_responses=True,
            max_connections=10,
        )

    # Create client from pool
    redis = Redis(connection_pool=_redis_pool)

    try:
        yield redis
    finally:
        await redis.aclose()


async def get_postgres() -> AsyncGenerator[asyncpg.Connection, None]:
    """
    Get PostgreSQL connection from pool.

    Yields:
        asyncpg.Connection: PostgreSQL connection

    Example:
        ```python
        @app.get("/example")
        async def example_route(conn: asyncpg.Connection = Depends(get_postgres)):
            result = await conn.fetchval("SELECT 1")
            return {"result": result}
        ```
    """
    global _postgres_pool

    settings = get_settings()

    # Initialize pool on first use
    if _postgres_pool is None:
        logger.info("Initializing PostgreSQL connection pool")
        _postgres_pool = await asyncpg.create_pool(
            str(settings.database_url),
            min_size=2,
            max_size=10,
            command_timeout=60,
        )

    # Acquire connection from pool
    async with _postgres_pool.acquire() as connection:
        yield connection


async def get_bigquery() -> AsyncGenerator[bigquery.Client, None]:
    """
    Get BigQuery client.

    Yields:
        bigquery.Client: BigQuery client

    Example:
        ```python
        @app.get("/example")
        async def example_route(bq: bigquery.Client = Depends(get_bigquery)):
            query = "SELECT 1 as value"
            results = bq.query(query).result()
            return {"rows": [dict(row) for row in results]}
        ```
    """
    global _bigquery_client

    settings = get_settings()

    # Initialize client on first use (reused across requests)
    if _bigquery_client is None:
        logger.info(f"Initializing BigQuery client for project: {settings.gcp_project_id}")
        _bigquery_client = bigquery.Client(project=settings.gcp_project_id)

    yield _bigquery_client


async def get_queue() -> AsyncGenerator[ArqRedis, None]:
    """
    Get arq queue client for background job processing.

    Yields:
        ArqRedis: arq Redis client for enqueuing jobs

    Example:
        ```python
        @app.post("/reports/{id}/generate")
        async def generate_report(
            report_id: str,
            queue: ArqRedis = Depends(get_queue)
        ):
            job = await queue.enqueue_job("generate_report", report_id)
            return {"job_id": job.job_id}
        ```
    """
    settings = get_settings()

    # Parse Redis URL to get host and port
    redis_url = str(settings.redis_url)
    # Extract host and port from URL like "redis://localhost:6379/0"
    parts = redis_url.replace("redis://", "").split("/")
    host_port = parts[0].split(":")
    host = host_port[0]
    port = int(host_port[1]) if len(host_port) > 1 else 6379
    database = int(parts[1]) if len(parts) > 1 else 0

    # Create arq Redis settings
    redis_settings = RedisSettings(
        host=host,
        port=port,
        database=database,
    )

    # Create pool
    pool = await create_pool(redis_settings)

    try:
        yield pool
    finally:
        await pool.aclose()


async def cleanup_dependencies():
    """
    Cleanup all global connection pools.

    Should be called on application shutdown.
    """
    global _redis_pool, _postgres_pool, _bigquery_client

    logger.info("Cleaning up dependency injection resources...")

    # Close Redis pool
    if _redis_pool is not None:
        await _redis_pool.aclose()
        _redis_pool = None
        logger.info("Redis pool closed")

    # Close PostgreSQL pool
    if _postgres_pool is not None:
        await _postgres_pool.close()
        _postgres_pool = None
        logger.info("PostgreSQL pool closed")

    # Close BigQuery client (synchronous)
    if _bigquery_client is not None:
        _bigquery_client.close()
        _bigquery_client = None
        logger.info("BigQuery client closed")

    logger.info("Dependency cleanup complete")
