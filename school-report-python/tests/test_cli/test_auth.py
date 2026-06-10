"""Tests for CLI auth commands."""

import pytest
from unittest.mock import patch
from typer.testing import CliRunner

from schoolreport.cli.app import app


runner = CliRunner()


class TestAuthWhoami:
    """Tests for auth whoami command."""

    def test_whoami_shows_identity(self):
        """Test whoami shows current identity."""
        with patch("schoolreport.cli.commands.auth.get_current_identity") as mock_identity:
            mock_identity.return_value = {
                "email": "test@example.com",
                "project": "test-project",
                "type": "service_account",
            }

            result = runner.invoke(app, ["auth", "whoami"])

            assert result.exit_code == 0
            assert "test@example.com" in result.stdout
            assert "test-project" in result.stdout

    def test_whoami_not_authenticated(self):
        """Test whoami when not authenticated."""
        with patch("schoolreport.cli.commands.auth.get_current_identity") as mock_identity:
            mock_identity.return_value = None

            result = runner.invoke(app, ["auth", "whoami"])

            assert result.exit_code == 0
            assert "no valid credentials" in result.stdout.lower()

    def test_whoami_shows_account_type(self):
        """Test whoami shows account type (service account vs user)."""
        with patch("schoolreport.cli.commands.auth.get_current_identity") as mock_identity:
            mock_identity.return_value = {
                "email": "sa@project.iam.gserviceaccount.com",
                "project": "my-project",
                "type": "service_account",
            }

            result = runner.invoke(app, ["auth", "whoami"])

            assert result.exit_code == 0
            assert "service" in result.stdout.lower()
