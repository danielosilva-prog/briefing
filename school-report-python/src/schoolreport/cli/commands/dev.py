"""Development commands for the CLI."""

import asyncio
import json
import time
from pathlib import Path
from typing import List, Optional

import typer
from rich.console import Console
from rich.table import Table

app = typer.Typer(help="Development commands")
console = Console()


def get_reports_dir() -> Path:
    """Get the reports directory."""
    candidates = [
        Path.cwd() / "reports",  # Python project uses 'reports' (plural)
        Path.cwd() / "report",   # R project uses 'report' (singular)
        Path(__file__).parent.parent.parent.parent.parent.parent / "report",
    ]
    for candidate in candidates:
        if candidate.exists():
            return candidate
    return Path.cwd() / "reports"


def get_registry():
    """Get a ReportRegistry instance."""
    from schoolreport.services.registry import ReportRegistry

    return ReportRegistry(get_reports_dir())


async def execute_queries(report, params: dict, query_filter: Optional[str] = None) -> dict:
    """
    Execute queries for a report.

    Args:
        report: Report definition
        params: Query parameters
        query_filter: Optional query name to run only that query

    Returns:
        Dict mapping query names to results
    """
    from schoolreport.config import get_settings
    from schoolreport.core.bigquery import BigQueryClient
    from schoolreport.models.report import SourceType

    settings = get_settings()
    bigquery_client = BigQueryClient(project_id=settings.gcp_project_id)

    results = {}
    report_dir = getattr(report, "_report_dir", None)

    queries_to_run = report.queries
    if query_filter:
        queries_to_run = [q for q in report.queries if q.name == query_filter]
        if not queries_to_run:
            raise ValueError(f"Query '{query_filter}' not found in report")

    for query in queries_to_run:
        # Load SQL
        if report_dir:
            sql_path = report_dir / query.file
        else:
            sql_path = Path(query.file)

        if not sql_path.exists():
            raise FileNotFoundError(f"SQL file not found: {sql_path}")

        sql = sql_path.read_text(encoding="utf-8")

        # Execute
        if query.source == SourceType.BIGQUERY:
            df = await bigquery_client.execute_query(sql, params)
            results[query.name] = df.to_dict(orient="records")
        else:
            raise ValueError(f"Unsupported source: {query.source}")

    return results


def parse_parameters(params: List[str]) -> dict:
    """Parse key=value parameters."""
    result = {}
    for param in params:
        if "=" not in param:
            raise ValueError(f"Invalid parameter format: '{param}'")
        key, value = param.split("=", 1)
        result[key.strip()] = value.strip()
    return result


@app.command()
def serve(
    port: int = typer.Option(8000, "--port", "-p", help="Port to listen on"),
    host: str = typer.Option("127.0.0.1", "--host", "-h", help="Host to bind to"),
    reload: bool = typer.Option(False, "--reload", "-r", help="Enable auto-reload"),
) -> None:
    """
    Start a local development server.

    This runs the FastAPI application locally for testing.
    """
    import uvicorn

    console.print(f"[bold]Starting development server...[/bold]")
    console.print(f"  Host: {host}")
    console.print(f"  Port: {port}")
    console.print(f"  Reload: {reload}")
    console.print(f"\n  URL: http://{host}:{port}")
    console.print(f"  Docs: http://{host}:{port}/docs\n")

    uvicorn.run(
        "schoolreport.api.app:app",
        host=host,
        port=port,
        reload=reload,
    )


@app.command()
def query(
    report_id: str = typer.Argument(..., help="Report ID"),
    params: Optional[List[str]] = typer.Argument(None, help="Parameters as key=value"),
    query_name: Optional[str] = typer.Option(
        None,
        "--query", "-q",
        help="Run only a specific query",
    ),
    format: str = typer.Option(
        "table",
        "--format", "-f",
        help="Output format: table or json",
    ),
    output: Optional[Path] = typer.Option(
        None,
        "--output", "-o",
        help="Write output to file",
    ),
) -> None:
    """
    Execute queries for a report and display results.

    This is useful for debugging queries without generating the full report.
    With ``--format json``, only the JSON payload is written to stdout (all
    status/progress/error messages are routed to stderr), so the output can be
    piped directly into tools like ``jq``. When combined with ``--query``, the
    payload is unwrapped to the rows array for that single query.

    Examples:
        schoolreport dev query ATM cod_ibge=2304400
        schoolreport dev query ATM cod_ibge=2304400 --query municipio
        schoolreport dev query ATM cod_ibge=2304400 --format json
        schoolreport dev query ATM-EQ cod_ibge=2927408 --query municipio_info --format json | jq '.[0]'
    """
    err_console = Console(stderr=True)

    try:
        # Parse parameters
        try:
            parsed_params = parse_parameters(params or [])
        except ValueError as e:
            err_console.print(f"[red]Error: {e}[/red]")
            raise typer.Exit(1)

        # Get report
        try:
            registry = get_registry()
            report = registry.get(report_id)
        except Exception as exc:
            from schoolreport.services.registry import ReportNotFoundError

            if not isinstance(exc, ReportNotFoundError):
                raise
            # fall through to handle ReportNotFoundError
            err_console.print(f"[red]Error: Report '{report_id}' not found.[/red]")
            raise typer.Exit(1)

        # Execute queries
        err_console.print(f"[bold]Running queries for {report_id}...[/bold]\n")
        start_time = time.time()

        try:
            results = asyncio.run(execute_queries(report, parsed_params, query_name))
        except Exception as e:
            err_console.print(f"[red]Error executing queries: {e}[/red]")
            raise typer.Exit(1)

        elapsed = time.time() - start_time

        # Output results
        if format == "json":
            if query_name is not None:
                # Single-query filter: emit just the rows array for clean piping.
                payload = results.get(query_name, [])
            else:
                payload = results
            json_output = json.dumps(payload, indent=2, default=str)
            if output:
                output.write_text(json_output)
                err_console.print(f"[green]✓ Results saved to: {output}[/green]")
            else:
                # Use plain print to avoid Rich markup parsing / soft-wrapping
                # that could corrupt the JSON when piped into tools like jq.
                print(json_output)
        else:
            # Table format
            for name, rows in results.items():
                err_console.print(f"[cyan]{name}[/cyan]: {len(rows)} rows")

                if rows:
                    # Show sample of data
                    table = Table(title=f"Sample: {name} (first 5 rows)")

                    # Add columns from first row
                    columns = list(rows[0].keys())[:10]  # Limit columns
                    for col in columns:
                        table.add_column(col, overflow="ellipsis", max_width=30)

                    # Add rows (max 5)
                    for row in rows[:5]:
                        values = [str(row.get(col, ""))[:30] for col in columns]
                        table.add_row(*values)

                    console.print(table)
                    console.print()

            if output:
                output.write_text(json.dumps(results, indent=2, default=str))
                err_console.print(f"[green]✓ Full results saved to: {output}[/green]")

        err_console.print(f"\n[dim]Total time: {elapsed:.2f}s[/dim]")

    except typer.Exit:
        raise
    except Exception as e:
        err_console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)
