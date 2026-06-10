"""Cache management commands."""

from pathlib import Path

import typer
from rich.console import Console

app = typer.Typer(no_args_is_help=True)
console = Console()


@app.command()
def info() -> None:
    """Show cache statistics."""
    from schoolreport.core.query_cache import QueryCache, DEFAULT_CACHE_DIR

    cache = QueryCache()
    console.print(cache.info())


@app.command()
def clear() -> None:
    """Clear all cached query results."""
    from schoolreport.core.query_cache import QueryCache

    cache = QueryCache()
    count = cache.clear()
    console.print(f"[green]Cleared {count} cache entries.[/green]")
