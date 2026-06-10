"""Reports management commands for the CLI."""

import json
import typer
from pathlib import Path
from typing import Optional
from rich.console import Console
from rich.table import Table
from rich.panel import Panel


app = typer.Typer(help="Report management commands")
console = Console()


def get_reports_dir() -> Path:
    """Get the reports directory."""
    # Look for reports/ directory in common locations
    candidates = [
        Path.cwd() / "reports",
        Path(__file__).resolve().parents[4] / "reports",
    ]
    for candidate in candidates:
        if candidate.exists():
            return candidate
    return Path.cwd() / "reports"


def get_registry():
    """Get a ReportRegistry instance."""
    from schoolreport.services.registry import ReportRegistry

    reports_dir = get_reports_dir()
    return ReportRegistry(reports_dir)


@app.command("list")
def list_reports(
    format: str = typer.Option(
        "table",
        "--format", "-f",
        help="Output format: table or json",
    ),
) -> None:
    """List all available reports."""
    try:
        registry = get_registry()
        reports = sorted(registry.get_all().values(), key=lambda report: report.id)

        if not reports:
            console.print("[yellow]No reports found.[/yellow]")
            console.print(f"Looking in: {get_reports_dir()}")
            return

        if format == "json":
            output = [
                {
                    "id": r.id,
                    "name": r.name,
                    "description": r.description or "",
                    "parameters": [p.name for p in r.parameters],
                }
                for r in reports
            ]
            console.print(json.dumps(output, indent=2))
        else:
            table = Table(title="Available Reports")
            table.add_column("ID", style="cyan", no_wrap=True)
            table.add_column("Name", style="green")
            table.add_column("Parameters", style="yellow")

            for report in reports:
                params = ", ".join(p.name for p in report.parameters) if report.parameters else "(none)"
                table.add_row(report.id, report.name, params)

            console.print(table)

    except Exception as e:
        console.print(f"[red]Error listing reports: {e}[/red]")
        raise typer.Exit(1)


@app.command("show")
def show_report(
    report_id: str = typer.Argument(..., help="Report ID to show"),
    format: str = typer.Option(
        "table",
        "--format", "-f",
        help="Output format: table or json",
    ),
) -> None:
    """Show details of a specific report."""
    try:
        registry = get_registry()
        report = registry.get(report_id)

        if format == "json":
            output = {
                "id": report.id,
                "name": report.name,
                "description": report.description or "",
                "version": report.version or "1.0.0",
                "parameters": [
                    {
                        "name": p.name,
                        "type": p.type.value,
                        "required": p.required,
                        "default": p.default,
                        "description": p.description or "",
                    }
                    for p in report.parameters
                ],
                "queries": [
                    {"name": q.name, "source": q.source.value, "file": q.file}
                    for q in report.queries
                ],
                "charts": [
                    {"name": c.name, "type": c.type.value}
                    for c in report.charts
                ],
            }
            console.print(json.dumps(output, indent=2))
        else:
            # Header panel
            console.print(Panel(
                f"[bold]{report.name}[/bold]\n{report.description or 'No description'}",
                title=f"Report: {report.id}",
                subtitle=f"v{report.version or '1.0.0'}",
            ))

            # Parameters table
            if report.parameters:
                params_table = Table(title="Parameters")
                params_table.add_column("Name", style="cyan")
                params_table.add_column("Type", style="yellow")
                params_table.add_column("Required", style="red")
                params_table.add_column("Default", style="green")
                params_table.add_column("Description")

                for p in report.parameters:
                    params_table.add_row(
                        p.name,
                        p.type.value,
                        "yes" if p.required else "no",
                        str(p.default) if p.default is not None else "-",
                        p.description or "-",
                    )
                console.print(params_table)
            else:
                console.print("[dim]No parameters required.[/dim]")

            # Queries table
            if report.queries:
                queries_table = Table(title="Queries")
                queries_table.add_column("Name", style="cyan")
                queries_table.add_column("Source", style="yellow")
                queries_table.add_column("File", style="dim")

                for q in report.queries:
                    queries_table.add_row(q.name, q.source.value, q.file)
                console.print(queries_table)

            # Charts
            if report.charts:
                charts_table = Table(title="Charts")
                charts_table.add_column("Name", style="cyan")
                charts_table.add_column("Type", style="yellow")
                charts_table.add_column("Data Source", style="dim")

                for c in report.charts:
                    charts_table.add_row(c.name, c.type.value, c.data)
                console.print(charts_table)

    except Exception as exc:
        from schoolreport.services.registry import ReportNotFoundError

        if not isinstance(exc, ReportNotFoundError):
            raise
        console.print(f"[red]Error: Report '{report_id}' not found.[/red]")
        console.print(f"Use 'schoolreport reports list' to see available reports.")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]Error showing report: {e}[/red]")
        raise typer.Exit(1)


@app.command("validate")
def validate_report(
    report_id: Optional[str] = typer.Argument(None, help="Report ID to validate (omit for all)"),
    all_reports: bool = typer.Option(
        False,
        "--all", "-a",
        help="Validate all reports",
    ),
) -> None:
    """Validate report definition(s)."""
    reports_dir = get_reports_dir()

    if not reports_dir.exists():
        console.print(f"[red]Error: Reports directory not found: {reports_dir}[/red]")
        raise typer.Exit(1)

    if all_reports or report_id is None:
        # Validate all reports
        report_dirs = [d for d in reports_dir.iterdir() if d.is_dir() and not d.name.startswith("_")]

        if not report_dirs:
            console.print("[yellow]No reports found to validate.[/yellow]")
            return

        all_valid = True
        for report_dir in sorted(report_dirs):
            rid = report_dir.name
            valid, errors = _validate_single_report(reports_dir, rid)
            if valid:
                console.print(f"[green]✓ {rid}[/green]")
            else:
                console.print(f"[red]✗ {rid}[/red]")
                for error in errors:
                    console.print(f"    [red]{error}[/red]")
                all_valid = False

        if not all_valid:
            raise typer.Exit(1)
    else:
        # Validate single report
        valid, errors = _validate_single_report(reports_dir, report_id)
        if valid:
            console.print(f"[green]✓ Report '{report_id}' is valid[/green]")
        else:
            console.print(f"[red]✗ Report '{report_id}' has errors:[/red]")
            for error in errors:
                console.print(f"  [red]- {error}[/red]")
            raise typer.Exit(1)


def _validate_single_report(reports_dir: Path, report_id: str) -> tuple[bool, list[str]]:
    """
    Validate a single report.

    Returns:
        Tuple of (is_valid, list_of_errors)
    """
    errors = []
    report_dir = reports_dir / report_id

    # Check directory exists
    if not report_dir.exists():
        return False, [f"Report directory not found: {report_dir}"]

    # Check report.yaml exists
    yaml_file = report_dir / "report.yaml"
    if not yaml_file.exists():
        return False, [f"report.yaml not found in {report_dir}"]

    # Try to parse report.yaml
    try:
        import yaml
        with open(yaml_file) as f:
            data = yaml.safe_load(f)
    except yaml.YAMLError as e:
        return False, [f"Invalid YAML: {e}"]
    except Exception as e:
        return False, [f"Error reading report.yaml: {e}"]

    # Validate required fields
    if not data.get("id"):
        errors.append("Missing 'id' field")
    if not data.get("name"):
        errors.append("Missing 'name' field")

    # Validate queries - check SQL files exist
    queries = data.get("queries", [])
    for q in queries:
        if isinstance(q, dict) and "file" in q:
            sql_file = report_dir / q["file"]
            if not sql_file.exists():
                errors.append(f"SQL file not found: {q['file']}")

    # Validate template exists
    template = data.get("template", {})
    if template:
        entry = template.get("entry")
        if entry:
            template_file = report_dir / entry
            if not template_file.exists():
                errors.append(f"Template file not found: {entry}")

    return len(errors) == 0, errors
