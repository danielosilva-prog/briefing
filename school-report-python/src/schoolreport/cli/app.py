"""CLI application entry point."""

import importlib
import logging

import typer
from rich.console import Console
from rich.logging import RichHandler


def _lazy_typer(module_path: str, attr: str) -> typer.Typer:
    """Import a Typer app lazily on first invocation."""
    mod = importlib.import_module(module_path)
    return getattr(mod, attr)


# Create main app
app = typer.Typer(
    name="schoolreport",
    help="School Report CLI - Generate education reports locally",
    no_args_is_help=True,
)

# Console for rich output
console = Console()


@app.callback(invoke_without_command=True)
def _callback(
    ctx: typer.Context,
    verbose: bool = typer.Option(
        False,
        "--verbose", "-v",
        help="Show detailed logs (cache hits, query execution, etc.)",
    ),
) -> None:
    """Main callback — configures logging and registers subcommands."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(message)s",
        datefmt="[%X]",
        handlers=[RichHandler(console=console, show_time=False, show_path=False)],
    )
    # Silence noisy third-party loggers
    logging.getLogger("google").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("matplotlib").setLevel(logging.WARNING)
    logging.getLogger("PIL").setLevel(logging.WARNING)

    if ctx.invoked_subcommand is None:
        # no_args_is_help handles this
        return


# Use a startup hook to register commands lazily right before dispatch.
# Typer needs the sub-apps registered before it resolves subcommands,
# so we register them at module level but import lazily via a wrapper.

def _register_commands() -> None:
    """Register all subcommands (imports happen here)."""
    from schoolreport.cli.commands import auth, cache, reports, generate, dev

    app.add_typer(auth.app, name="auth", help="Authentication commands")
    app.add_typer(cache.app, name="cache", help="Query cache management")
    app.add_typer(reports.app, name="reports", help="Report management commands")
    app.add_typer(dev.app, name="dev", help="Development commands")
    app.command(name="generate")(generate.generate)


def main():
    """Entry point for the CLI."""
    _register_commands()
    app()


if __name__ == "__main__":
    main()
