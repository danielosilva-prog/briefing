"""Authentication commands for the CLI."""

import json
import typer
from pathlib import Path
from typing import Optional, Tuple
from rich.console import Console
from rich.table import Table

from google.auth import default as google_default
from google.auth.exceptions import DefaultCredentialsError
from google.oauth2 import service_account

app = typer.Typer(help="Authentication commands")
console = Console()


def get_config_dir() -> Path:
    """Get the config directory for schoolreport CLI."""
    config_dir = Path.home() / ".schoolreport"
    config_dir.mkdir(exist_ok=True)
    return config_dir


def get_config_file() -> Path:
    """Get the config file path."""
    return get_config_dir() / "config.json"


def load_config() -> dict:
    """Load config from file."""
    config_file = get_config_file()
    if config_file.exists():
        return json.loads(config_file.read_text())
    return {}


def authenticate_service_account(credentials_path: Path) -> Tuple[str, str]:
    """
    Authenticate using a service account credentials file.

    Args:
        credentials_path: Path to the service account JSON file

    Returns:
        Tuple of (email, project_id)

    Raises:
        ValueError: If credentials are invalid
    """
    try:
        creds_data = json.loads(credentials_path.read_text())
        credentials = service_account.Credentials.from_service_account_file(
            str(credentials_path),
            scopes=[
                "https://www.googleapis.com/auth/bigquery.readonly",
                "https://www.googleapis.com/auth/cloud-platform",
            ],
        )
        email = creds_data.get("client_email", "unknown")
        project = creds_data.get("project_id", "unknown")
        return email, project
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in credentials file: {e}")
    except Exception as e:
        raise ValueError(f"Failed to load credentials: {e}")


def authenticate_browser() -> Tuple[str, str]:
    """
    Authenticate using browser-based SSO (Application Default Credentials).

    Returns:
        Tuple of (email, project_id)

    Raises:
        ValueError: If authentication fails
    """
    try:
        credentials, project = google_default(
            scopes=[
                "https://www.googleapis.com/auth/bigquery.readonly",
                "https://www.googleapis.com/auth/cloud-platform",
            ]
        )
        # Try to get email from credentials
        email = getattr(credentials, "service_account_email", None)
        if not email:
            email = getattr(credentials, "_account", "user@localhost")
        return email, project or "default"
    except DefaultCredentialsError as e:
        raise ValueError(f"No credentials found. Run 'gcloud auth application-default login' first: {e}")


def get_current_identity() -> Optional[dict]:
    """
    Get the current authenticated identity.

    Returns:
        Dict with identity info, or None if not authenticated
    """
    config = load_config()

    # Check if we have a saved credentials path
    creds_path = config.get("credentials_path")
    if creds_path:
        try:
            path = Path(creds_path)
            if path.exists():
                email, project = authenticate_service_account(path)
                return {
                    "email": email,
                    "project": project,
                    "type": "service_account",
                    "credentials_path": creds_path,
                }
        except Exception:
            pass

    # Try Application Default Credentials
    try:
        email, project = authenticate_browser()
        return {
            "email": email,
            "project": project,
            "type": "user" if "@" in email and "iam.gserviceaccount.com" not in email else "service_account",
        }
    except Exception:
        return None


@app.command()
def whoami() -> None:
    """Show current authenticated identity."""
    identity = get_current_identity()

    if identity is None:
        console.print("[yellow]No valid credentials found.[/yellow]")
        console.print("\nTo authenticate, set GOOGLE_APPLICATION_CREDENTIALS:")
        console.print("  export GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.json")
        raise typer.Exit(0)

    table = Table(title="Current Identity", show_header=False)
    table.add_column("Key", style="cyan")
    table.add_column("Value", style="green")

    table.add_row("Email", identity["email"])
    table.add_row("Project", identity["project"])
    table.add_row("Type", identity["type"])

    if "credentials_path" in identity:
        table.add_row("Credentials", identity["credentials_path"])

    console.print(table)
