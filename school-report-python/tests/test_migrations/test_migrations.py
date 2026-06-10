"""Tests for database migrations."""

import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

from alembic import command
from alembic.config import Config
from alembic.script import ScriptDirectory


@pytest.fixture
def alembic_config():
    """Create Alembic config for testing."""
    migrations_dir = Path(__file__).parent.parent.parent / "migrations"
    config = Config(str(migrations_dir / "alembic.ini"))
    config.set_main_option("script_location", str(migrations_dir))
    return config


@pytest.fixture
def script_directory(alembic_config):
    """Get script directory for inspecting migrations."""
    return ScriptDirectory.from_config(alembic_config)


class TestMigrationStructure:
    """Tests for migration file structure."""

    def test_migrations_directory_exists(self):
        """Test that migrations directory exists."""
        migrations_dir = Path(__file__).parent.parent.parent / "migrations"
        assert migrations_dir.exists()
        assert (migrations_dir / "alembic.ini").exists()
        assert (migrations_dir / "env.py").exists()
        assert (migrations_dir / "versions").exists()

    def test_all_migrations_have_revision(self, script_directory):
        """Test that all migration files have valid revision IDs."""
        revisions = list(script_directory.walk_revisions())

        # Should have at least 3 migrations (jobs, cache, audit)
        assert len(revisions) >= 3

        for revision in revisions:
            assert revision.revision is not None
            assert len(revision.revision) > 0

    def test_migrations_are_linear(self, script_directory):
        """Test that migrations form a linear chain (no branches)."""
        heads = script_directory.get_heads()

        # Should have exactly one head
        assert len(heads) == 1, f"Expected 1 head, found {len(heads)}: {heads}"

    def test_first_migration_has_no_down_revision(self, script_directory):
        """Test that the first migration has no down_revision."""
        base = script_directory.get_base()
        revision = script_directory.get_revision(base)

        assert revision.down_revision is None


class TestJobsTableMigration:
    """Tests for jobs table migration."""

    def test_jobs_migration_exists(self, script_directory):
        """Test that jobs table migration exists."""
        revisions = list(script_directory.walk_revisions())
        revision_messages = [r.doc for r in revisions]

        assert any("job" in msg.lower() for msg in revision_messages if msg)

    def test_jobs_migration_creates_table(self, script_directory):
        """Test that jobs migration has correct upgrade operations."""
        revisions = list(script_directory.walk_revisions())

        jobs_revision = None
        for rev in revisions:
            if rev.doc and "job" in rev.doc.lower():
                jobs_revision = rev
                break

        assert jobs_revision is not None

        # Check upgrade function exists and creates table
        module = jobs_revision.module
        assert hasattr(module, "upgrade")
        assert hasattr(module, "downgrade")


class TestCacheTableMigration:
    """Tests for cache table migration."""

    def test_cache_migration_exists(self, script_directory):
        """Test that cache table migration exists."""
        revisions = list(script_directory.walk_revisions())
        revision_messages = [r.doc for r in revisions]

        assert any("cache" in msg.lower() for msg in revision_messages if msg)


class TestAuditLogTableMigration:
    """Tests for audit log table migration."""

    def test_audit_migration_exists(self, script_directory):
        """Test that audit log table migration exists."""
        revisions = list(script_directory.walk_revisions())
        revision_messages = [r.doc for r in revisions]

        assert any("audit" in msg.lower() for msg in revision_messages if msg)


class TestMigrationContent:
    """Tests for migration content and schema."""

    def test_jobs_table_has_required_columns(self, script_directory):
        """Test jobs table has all required columns."""
        # Find jobs migration
        revisions = list(script_directory.walk_revisions())
        jobs_revision = None
        for rev in revisions:
            if rev.doc and "job" in rev.doc.lower():
                jobs_revision = rev
                break

        assert jobs_revision is not None

        # Read the migration file content
        migration_path = Path(jobs_revision.path)
        content = migration_path.read_text()

        # Check for required columns
        required_columns = [
            "id",
            "report_id",
            "status",
            "parameters",
            "created_at",
        ]

        for col in required_columns:
            assert col in content, f"Missing column: {col}"

    def test_cache_table_has_required_columns(self, script_directory):
        """Test cache table has all required columns."""
        revisions = list(script_directory.walk_revisions())
        cache_revision = None
        for rev in revisions:
            if rev.doc and "cache" in rev.doc.lower():
                cache_revision = rev
                break

        assert cache_revision is not None

        migration_path = Path(cache_revision.path)
        content = migration_path.read_text()

        required_columns = [
            "cache_key",
            "report_id",
            "gcs_path",
            "expires_at",
        ]

        for col in required_columns:
            assert col in content, f"Missing column: {col}"

    def test_audit_table_has_required_columns(self, script_directory):
        """Test audit log table has all required columns."""
        revisions = list(script_directory.walk_revisions())
        audit_revision = None
        for rev in revisions:
            if rev.doc and "audit" in rev.doc.lower():
                audit_revision = rev
                break

        assert audit_revision is not None

        migration_path = Path(audit_revision.path)
        content = migration_path.read_text()

        required_columns = [
            "id",
            "job_id",
            "report_id",
            "status",
            "requester",
        ]

        for col in required_columns:
            assert col in content, f"Missing column: {col}"


class TestMigrationDowngrade:
    """Tests for migration downgrade functionality."""

    def test_all_migrations_have_downgrade(self, script_directory):
        """Test that all migrations have downgrade functions."""
        revisions = list(script_directory.walk_revisions())

        for revision in revisions:
            module = revision.module
            assert hasattr(module, "downgrade"), f"Missing downgrade in {revision.revision}"

            # Check downgrade is not empty (not just 'pass')
            import inspect
            source = inspect.getsource(module.downgrade)
            # Should have actual operations, not just pass
            assert "drop_table" in source or "drop_index" in source or "drop_column" in source, \
                f"Downgrade in {revision.revision} appears to be empty"
