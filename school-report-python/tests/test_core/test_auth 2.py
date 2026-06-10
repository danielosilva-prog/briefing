"""Tests for authentication module."""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from schoolreport.core.auth import (
    AuthManager,
    AuthenticationError,
    CredentialSource,
)


class TestAuthManager:
    """Test AuthManager class."""

    def test_init_default(self):
        """Test AuthManager initialization with defaults."""
        auth = AuthManager()
        assert auth.project_id is None
        assert auth.credentials is None

    def test_init_with_project_id(self):
        """Test AuthManager initialization with project ID."""
        auth = AuthManager(project_id="test-project")
        assert auth.project_id == "test-project"

    @patch("schoolreport.core.auth.service_account.Credentials.from_service_account_file")
    def test_load_from_service_account_file(self, mock_from_file):
        """Test loading credentials from service account file."""
        mock_creds = Mock()
        mock_from_file.return_value = mock_creds

        auth = AuthManager()
        result = auth.load_from_service_account_file("/path/to/credentials.json")

        assert result is True
        assert auth.credentials == mock_creds
        assert auth.credential_source == CredentialSource.SERVICE_ACCOUNT_FILE
        mock_from_file.assert_called_once()

    @patch("schoolreport.core.auth.service_account.Credentials.from_service_account_file")
    def test_load_from_service_account_file_not_found(self, mock_from_file):
        """Test loading credentials from non-existent file."""
        mock_from_file.side_effect = FileNotFoundError()

        auth = AuthManager()
        result = auth.load_from_service_account_file("/path/to/missing.json")

        assert result is False
        assert auth.credentials is None

    @patch.dict("os.environ", {"GOOGLE_APPLICATION_CREDENTIALS": "/path/to/creds.json"})
    @patch("schoolreport.core.auth.service_account.Credentials.from_service_account_file")
    def test_load_from_environment_variable(self, mock_from_file):
        """Test loading credentials from GOOGLE_APPLICATION_CREDENTIALS."""
        mock_creds = Mock()
        mock_from_file.return_value = mock_creds

        auth = AuthManager()
        result = auth.load_from_environment()

        assert result is True
        assert auth.credentials == mock_creds
        assert auth.credential_source == CredentialSource.ENVIRONMENT_VARIABLE

    @patch.dict("os.environ", {}, clear=True)
    def test_load_from_environment_variable_not_set(self):
        """Test loading from environment when variable not set."""
        auth = AuthManager()
        result = auth.load_from_environment()

        assert result is False
        assert auth.credentials is None

    @patch("schoolreport.core.auth.Path.exists")
    @patch("schoolreport.core.auth.service_account.Credentials.from_service_account_file")
    def test_load_from_local_file(self, mock_from_file, mock_exists):
        """Test loading credentials from .gcp-credentials.json."""
        mock_exists.return_value = True
        mock_creds = Mock()
        mock_from_file.return_value = mock_creds

        auth = AuthManager()
        result = auth.load_from_local_file()

        assert result is True
        assert auth.credentials == mock_creds
        assert auth.credential_source == CredentialSource.LOCAL_FILE

    @patch("schoolreport.core.auth.Path.exists")
    def test_load_from_local_file_not_exists(self, mock_exists):
        """Test loading from local file when it doesn't exist."""
        mock_exists.return_value = False

        auth = AuthManager()
        result = auth.load_from_local_file()

        assert result is False
        assert auth.credentials is None

    @patch("schoolreport.core.auth.requests.get")
    @patch("schoolreport.core.auth.compute_engine.Credentials")
    def test_load_from_metadata_server(self, mock_compute_creds, mock_get):
        """Test loading credentials from GCP metadata server."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        mock_creds = Mock()
        mock_compute_creds.return_value = mock_creds

        auth = AuthManager()
        result = auth.load_from_metadata_server()

        assert result is True
        assert auth.credentials == mock_creds
        assert auth.credential_source == CredentialSource.METADATA_SERVER

    @patch("schoolreport.core.auth.requests.get")
    def test_load_from_metadata_server_not_available(self, mock_get):
        """Test loading from metadata server when not in GCP."""
        mock_get.side_effect = Exception("Connection refused")

        auth = AuthManager()
        result = auth.load_from_metadata_server()

        assert result is False
        assert auth.credentials is None

    @patch.dict("os.environ", {"GOOGLE_APPLICATION_CREDENTIALS": "/path/to/creds.json"})
    @patch("schoolreport.core.auth.service_account.Credentials.from_service_account_file")
    def test_authenticate_auto_success(self, mock_from_file):
        """Test automatic authentication succeeds."""
        mock_creds = Mock()
        mock_from_file.return_value = mock_creds

        auth = AuthManager()
        auth.authenticate()

        assert auth.is_authenticated() is True
        assert auth.credentials is not None

    @patch.dict("os.environ", {}, clear=True)
    @patch("schoolreport.core.auth.Path.exists", return_value=False)
    @patch("schoolreport.core.auth.requests.get")
    def test_authenticate_auto_failure(self, mock_get, mock_exists):
        """Test automatic authentication fails when no credentials available."""
        mock_get.side_effect = Exception("No metadata server")

        auth = AuthManager()

        with pytest.raises(AuthenticationError, match="No credentials found"):
            auth.authenticate()

    def test_is_authenticated_false(self):
        """Test is_authenticated returns False when no credentials."""
        auth = AuthManager()
        assert auth.is_authenticated() is False

    @patch("schoolreport.core.auth.service_account.Credentials.from_service_account_file")
    def test_is_authenticated_true(self, mock_from_file):
        """Test is_authenticated returns True when credentials loaded."""
        mock_creds = Mock()
        mock_from_file.return_value = mock_creds

        auth = AuthManager()
        auth.load_from_service_account_file("/path/to/creds.json")

        assert auth.is_authenticated() is True

    @patch("schoolreport.core.auth.service_account.Credentials.from_service_account_file")
    def test_get_credentials(self, mock_from_file):
        """Test get_credentials returns credentials."""
        mock_creds = Mock()
        mock_creds.project_id = "test-project"
        mock_from_file.return_value = mock_creds

        auth = AuthManager()
        auth.load_from_service_account_file("/path/to/creds.json")

        creds = auth.get_credentials()
        assert creds == mock_creds

    def test_get_credentials_not_authenticated(self):
        """Test get_credentials raises error when not authenticated."""
        auth = AuthManager()

        with pytest.raises(AuthenticationError, match="Not authenticated"):
            auth.get_credentials()

    @patch("schoolreport.core.auth.service_account.Credentials.from_service_account_file")
    def test_get_identity(self, mock_from_file):
        """Test get_identity returns service account email."""
        mock_creds = Mock()
        mock_creds.service_account_email = "test@test-project.iam.gserviceaccount.com"
        mock_from_file.return_value = mock_creds

        auth = AuthManager()
        auth.load_from_service_account_file("/path/to/creds.json")

        identity = auth.get_identity()
        assert identity == "test@test-project.iam.gserviceaccount.com"

    def test_get_identity_not_authenticated(self):
        """Test get_identity returns None when not authenticated."""
        auth = AuthManager()
        assert auth.get_identity() is None

    @patch("schoolreport.core.auth.service_account.Credentials.from_service_account_file")
    def test_credential_source_tracking(self, mock_from_file):
        """Test that credential source is properly tracked."""
        mock_creds = Mock()
        mock_from_file.return_value = mock_creds

        auth = AuthManager()
        auth.load_from_service_account_file("/path/to/creds.json")

        assert auth.credential_source == CredentialSource.SERVICE_ACCOUNT_FILE
        assert str(auth.credential_source) == "service_account_file"
