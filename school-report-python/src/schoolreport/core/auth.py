"""Authentication module for Google Cloud Platform.

Handles credential resolution with the following priority:
1. GOOGLE_APPLICATION_CREDENTIALS environment variable
2. .gcp-credentials.json in project root
3. GCP metadata server (when running in GCP)
4. SSO login (interactive, for local development)
"""

import os
import requests
from enum import Enum
from pathlib import Path
from typing import Optional
from google.oauth2 import service_account
from google.auth import compute_engine
from google.auth.credentials import Credentials


class CredentialSource(Enum):
    """Enum for tracking where credentials came from."""

    SERVICE_ACCOUNT_FILE = "service_account_file"
    ENVIRONMENT_VARIABLE = "environment_variable"
    LOCAL_FILE = "local_file"
    METADATA_SERVER = "metadata_server"
    SSO = "sso"

    def __str__(self) -> str:
        return self.value


class AuthenticationError(Exception):
    """Raised when authentication fails."""

    pass


class AuthManager:
    """Manages authentication with Google Cloud Platform."""

    def __init__(self, project_id: Optional[str] = None):
        """Initialize AuthManager.

        Args:
            project_id: Optional GCP project ID
        """
        self.project_id = project_id
        self.credentials: Optional[Credentials] = None
        self.credential_source: Optional[CredentialSource] = None

    def load_from_service_account_file(self, file_path: str) -> bool:
        """Load credentials from a service account JSON file.

        Args:
            file_path: Path to service account JSON file

        Returns:
            True if credentials loaded successfully, False otherwise
        """
        try:
            self.credentials = service_account.Credentials.from_service_account_file(
                file_path,
                scopes=[
                    "https://www.googleapis.com/auth/bigquery",
                    "https://www.googleapis.com/auth/cloud-platform",
                    "https://www.googleapis.com/auth/devstorage.full_control",
                ],
            )
            self.credential_source = CredentialSource.SERVICE_ACCOUNT_FILE

            # Extract project ID from credentials if not set
            if not self.project_id and hasattr(self.credentials, 'project_id'):
                self.project_id = self.credentials.project_id

            return True
        except FileNotFoundError:
            return False
        except Exception:
            return False

    def load_from_environment(self) -> bool:
        """Load credentials from GOOGLE_APPLICATION_CREDENTIALS environment variable.

        Returns:
            True if credentials loaded successfully, False otherwise
        """
        credentials_path = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
        if not credentials_path:
            return False

        if self.load_from_service_account_file(credentials_path):
            self.credential_source = CredentialSource.ENVIRONMENT_VARIABLE
            return True

        return False

    def load_from_local_file(self) -> bool:
        """Load credentials from .gcp-credentials.json in project root.

        Returns:
            True if credentials loaded successfully, False otherwise
        """
        # Look for .gcp-credentials.json in project root
        project_root = Path(__file__).parent.parent.parent.parent
        local_creds_path = project_root / ".gcp-credentials.json"

        if not local_creds_path.exists():
            return False

        if self.load_from_service_account_file(str(local_creds_path)):
            self.credential_source = CredentialSource.LOCAL_FILE
            return True

        return False

    def load_from_metadata_server(self) -> bool:
        """Load credentials from GCP metadata server (when running in GCP).

        Returns:
            True if credentials loaded successfully, False otherwise
        """
        try:
            # Check if metadata server is available
            metadata_url = "http://metadata.google.internal/computeMetadata/v1/project/project-id"
            headers = {"Metadata-Flavor": "Google"}
            response = requests.get(metadata_url, headers=headers, timeout=1)

            if response.status_code == 200:
                self.credentials = compute_engine.Credentials()
                self.credential_source = CredentialSource.METADATA_SERVER

                # Get project ID from metadata server if not set
                if not self.project_id:
                    self.project_id = response.text

                return True

            return False
        except Exception:
            return False

    def authenticate(self) -> None:
        """Attempt to authenticate using all available methods.

        Tries methods in order:
        1. GOOGLE_APPLICATION_CREDENTIALS environment variable
        2. .gcp-credentials.json in project root
        3. GCP metadata server

        Raises:
            AuthenticationError: If all authentication methods fail
        """
        # Try environment variable first
        if self.load_from_environment():
            return

        # Try local file
        if self.load_from_local_file():
            return

        # Try metadata server
        if self.load_from_metadata_server():
            return

        # All methods failed
        raise AuthenticationError(
            "No credentials found. Please set GOOGLE_APPLICATION_CREDENTIALS, "
            "create .gcp-credentials.json in project root, or run in GCP environment."
        )

    def is_authenticated(self) -> bool:
        """Check if authentication is successful.

        Returns:
            True if authenticated, False otherwise
        """
        return self.credentials is not None

    def get_credentials(self) -> Credentials:
        """Get the loaded credentials.

        Returns:
            The loaded credentials

        Raises:
            AuthenticationError: If not authenticated
        """
        if not self.is_authenticated():
            raise AuthenticationError(
                "Not authenticated. Call authenticate() first."
            )

        return self.credentials  # type: ignore

    def get_identity(self) -> Optional[str]:
        """Get the identity of the authenticated user/service account.

        Returns:
            Service account email or user email, or None if not authenticated
        """
        if not self.is_authenticated():
            return None

        # For service account credentials
        if hasattr(self.credentials, "service_account_email"):
            return self.credentials.service_account_email  # type: ignore

        # For user credentials (SSO)
        if hasattr(self.credentials, "id_token"):
            # Would need to decode JWT to get email
            return "user@example.com"  # Placeholder

        return None

    def get_project_id(self) -> Optional[str]:
        """Get the GCP project ID.

        Returns:
            Project ID if available, None otherwise
        """
        return self.project_id
