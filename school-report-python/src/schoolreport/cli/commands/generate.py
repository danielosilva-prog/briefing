"""Generate command for the CLI."""

import asyncio
import json
import platform
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional

import typer
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn

console = Console()


def get_reports_dir() -> Path:
    """Get the reports directory."""
    candidates = [
        Path.cwd() / "reports",  # Python project uses 'reports' (plural)
        Path.cwd() / "report",   # R project uses 'report' (singular)
        Path(__file__).parent.parent.parent.parent.parent.parent / "reports",
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


def open_file(path: Path) -> None:
    """Open a file with the default system application."""
    system = platform.system()
    try:
        if system == "Darwin":  # macOS
            subprocess.run(["open", str(path)], check=True)
        elif system == "Linux":
            subprocess.run(["xdg-open", str(path)], check=True)
        elif system == "Windows":
            subprocess.run(["start", "", str(path)], shell=True, check=True)
    except subprocess.CalledProcessError:
        console.print(f"[yellow]Could not open file automatically.[/yellow]")


def parse_parameters(params: List[str]) -> dict:
    """
    Parse parameters from key=value format.

    Args:
        params: List of "key=value" strings

    Returns:
        Dict of parameter name to value (values may contain commas for batch mode)

    Raises:
        ValueError: If parameter format is invalid
    """
    result = {}
    for param in params:
        if "=" not in param:
            raise ValueError(f"Invalid parameter format: '{param}'. Expected 'key=value'.")
        key, value = param.split("=", 1)
        result[key.strip()] = value.strip()
    return result


@dataclass
class BatchSpec:
    """Describes a batch of parameter combinations to execute."""
    combinations: List[dict]  # Each element is a single-run dict[str, str]
    is_batch: bool            # True if more than one combination


def expand_batch_params(parsed: dict) -> BatchSpec:
    """
    Given a dict of str->str params (possibly with comma-separated values),
    return a BatchSpec describing all combinations to execute.

    Rules:
    - If any value contains a comma, it is a multi-value parameter.
    - All multi-value parameters must have the same count.
    - Multi-value params are zipped, not cartesian-producted.
    - If no multi-value params exist, a single-item BatchSpec is returned.

    Raises:
        ValueError: If multi-value params have different lengths.
    """
    single_values: dict = {}
    multi_values: dict = {}

    for key, value in parsed.items():
        parts = [v.strip() for v in value.split(",")]
        if len(parts) > 1:
            multi_values[key] = parts
        else:
            single_values[key] = value

    if not multi_values:
        return BatchSpec(combinations=[parsed], is_batch=False)

    lengths = {k: len(v) for k, v in multi_values.items()}
    if len(set(lengths.values())) > 1:
        detail = ", ".join(f"{k}={v}" for k, v in lengths.items())
        raise ValueError(
            f"Multi-value parameters must have the same number of values. Got: {detail}"
        )

    count = next(iter(lengths.values()))
    combinations = [
        {**single_values, **{k: multi_values[k][i] for k in multi_values}}
        for i in range(count)
    ]
    return BatchSpec(combinations=combinations, is_batch=True)


def _default_output(report_id: str, parsed_params: dict, data_only: bool) -> Path:
    """Compute the default output path for a single report."""
    output_dir = Path.cwd() / "output"
    output_dir.mkdir(exist_ok=True)
    param_parts = [f"{v}" for k, v in sorted(parsed_params.items())]
    param_str = "-".join(param_parts) if param_parts else "Brasil"
    ext = ".json" if data_only else ".pdf"
    return output_dir / f"{report_id}-{param_str}{ext}"


def _resolve_output_for_batch(
    output: Optional[Path],
    report_id: str,
    combo: dict,
    data_only: bool,
) -> Path:
    """
    Resolve the output path for a single item within a batch run.

    If ``--output`` was given it is treated as a directory.
    Each file is placed inside it with an auto-generated name.
    """
    ext = ".json" if data_only else ".pdf"
    param_parts = [f"{v}" for k, v in sorted(combo.items())]
    param_str = "-".join(param_parts) if param_parts else "Brasil"
    filename = f"{report_id}-{param_str}{ext}"
    output_dir = output if output is not None else Path.cwd() / "output"
    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir / filename


def _run_single_generate(
    *,
    report,
    report_id: str,
    parsed_params: dict,
    output: Path,
    data: Optional[Path],
    data_only: bool,
    upload: bool,
    open_after: bool,
    keep_chart_files: bool,
    no_cache: bool,
    label: str = "",
) -> Path:
    """
    Execute a single report generation.

    Args:
        label: Optional prefix for console messages, e.g. "[1/3]" in batch mode.

    Returns:
        The resolved output path.

    Raises:
        typer.Exit: On any error.
    """
    from schoolreport.cli.executor import LocalExecutor, discover_custom_executor

    prefix = f"{label} " if label else ""

    def _make_executor() -> LocalExecutor:
        return LocalExecutor(cache_enabled=not no_cache)

    console.print(f"{prefix}[bold]Generating report: {report_id}[/bold]")
    console.print(f"{prefix}Parameters: {parsed_params}")
    if data:
        console.print(f"{prefix}Data file: {data}")
    console.print(f"{prefix}Output: {output}\n")

    # --data mode: use JSON file instead of BigQuery
    if data is not None:
        if data_only:
            console.print(f"[red]{prefix}Error: --data and --data-only cannot be used together.[/red]")
            raise typer.Exit(1)

        try:
            json_data = json.loads(data.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError) as e:
            console.print(f"[red]{prefix}Error loading data file: {e}[/red]")
            raise typer.Exit(1)

        reports_dir = get_reports_dir()
        custom_executor_cls = discover_custom_executor(reports_dir / report_id)

        if custom_executor_cls is not None:
            console.print(f"{prefix}Using custom executor: {custom_executor_cls.__name__}")
            custom_executor = custom_executor_cls(reports_dir)

            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                TimeElapsedColumn(),
                console=console,
            ) as progress:
                task = progress.add_task(f"{prefix}Generating report with custom executor...", total=None)
                pdf_bytes = asyncio.run(custom_executor.execute(json_data))
                progress.update(task, description=f"{prefix}Done!")

            output.parent.mkdir(parents=True, exist_ok=True)
            output.write_bytes(pdf_bytes)
            console.print(f"\n[green]✓ {prefix}Report saved to: {output}[/green]")
        else:
            executor = _make_executor()

            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                TimeElapsedColumn(),
                console=console,
            ) as progress:
                result_path = asyncio.run(executor.execute_with_data(
                    report=report,
                    data=json_data,
                    params=parsed_params,
                    output=output,
                    progress=progress,
                    keep_chart_files=keep_chart_files,
                ))

            console.print(f"\n[green]✓ {prefix}Report saved to: {result_path}[/green]")

        if upload:
            executor = _make_executor()
            console.print(f"\n{prefix}Uploading to GCS...")
            gcs_path = asyncio.run(executor.upload(
                local_path=output,
                report_id=report_id,
                params=parsed_params,
            ))
            console.print(f"[green]✓ {prefix}Uploaded to: {gcs_path}[/green]")

        if open_after:
            open_file(output)

        return output

    elif data_only:
        executor = _make_executor()

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            TimeElapsedColumn(),
            console=console,
        ) as progress:
            task = progress.add_task(f"{prefix}Executing queries...", total=None)
            result = asyncio.run(executor.execute_data_only(
                report=report,
                params=parsed_params,
            ))
            progress.update(task, description=f"{prefix}Done!")

        output.write_text(json.dumps(result, indent=2, default=str))
        console.print(f"\n[green]✓ {prefix}Data saved to: {output}[/green]")
        return output

    else:
        reports_dir = get_reports_dir()
        custom_executor_cls = discover_custom_executor(reports_dir / report_id)

        if custom_executor_cls is not None:
            console.print(f"{prefix}Using custom executor: {custom_executor_cls.__name__}")
            custom_executor = custom_executor_cls(reports_dir)

            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                TimeElapsedColumn(),
                console=console,
            ) as progress:
                if report.queries:
                    executor = _make_executor()
                    task = progress.add_task(f"{prefix}Executing queries...", total=None)
                    query_data = asyncio.run(executor.execute_data_only(
                        report=report,
                        params=parsed_params,
                    ))
                    progress.update(task, description=f"{prefix}Rendering report...")
                else:
                    task = progress.add_task(f"{prefix}Rendering report...", total=None)
                    query_data = {}

                json_data = {
                    "metadata": {},
                    "params": parsed_params,
                    "queries": query_data,
                    "charts": {},
                    "template_params": {},
                    "keep_chart_files": keep_chart_files,
                }
                pdf_bytes = asyncio.run(custom_executor.execute(json_data))
                progress.update(task, description=f"{prefix}Done!")

            output.parent.mkdir(parents=True, exist_ok=True)
            output.write_bytes(pdf_bytes)
            result_path = output
        else:
            executor = _make_executor()
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                TimeElapsedColumn(),
                console=console,
            ) as progress:
                result_path = asyncio.run(executor.execute(
                    report=report,
                    params=parsed_params,
                    output=output,
                    progress=progress,
                    keep_chart_files=keep_chart_files,
                ))

        console.print(f"\n[green]✓ {prefix}Report saved to: {result_path}[/green]")

        if upload:
            console.print(f"\n{prefix}Uploading to GCS...")
            gcs_path = asyncio.run(executor.upload(
                local_path=result_path,
                report_id=report_id,
                params=parsed_params,
            ))
            console.print(f"[green]✓ {prefix}Uploaded to: {gcs_path}[/green]")

        if open_after:
            open_file(result_path)

        return result_path


def generate(
    report_id: str = typer.Argument(..., help="Report ID to generate"),
    params: Optional[List[str]] = typer.Argument(
        None,
        help="Report parameters as key=value pairs. Use comma-separated values for batch mode, e.g. cod_ibge=111,222,333",
    ),
    output: Optional[Path] = typer.Option(
        None,
        "--output", "-o",
        help="Output file path (single mode) or output directory (batch mode). Default: ./output/{report_id}-{params}.pdf",
    ),
    data_only: bool = typer.Option(
        False,
        "--data-only",
        help="Output JSON data only (no PDF generation)",
    ),
    upload: bool = typer.Option(
        False,
        "--upload",
        help="Upload to GCS after generation",
    ),
    data: Optional[Path] = typer.Option(
        None,
        "--data",
        help="Path to a JSON data file to use instead of BigQuery queries",
        exists=True,
        readable=True,
    ),
    no_cache: bool = typer.Option(
        False,
        "--no-cache",
        help="Disable query cache for this execution (always hit BigQuery)",
    ),
    open_after: bool = typer.Option(
        False,
        "--open",
        help="Open the PDF after generation",
    ),
    keep_chart_files: bool = typer.Option(
        False,
        "--keep-chart-files",
        help="Preserve temporary .chart_*.svg and .data_*.json files generated during Typst rendering",
    ),
) -> None:
    """
    Generate a report locally.

    Examples:
        schoolreport generate ATM cod_ibge=2304400 ano=2024
        schoolreport generate ATM cod_ibge=111,222,333 ano=2024
        schoolreport generate ATM cod_ibge=111,222 ano=2023,2024
        schoolreport generate ATM cod_ibge=2304400 --output report.pdf
        schoolreport generate ATM cod_ibge=2304400 --data-only --output data.json
        schoolreport generate ATM cod_ibge=2304400 --upload
        schoolreport generate ATS-02 sigla=UFAL --data reports/ATS-02/data/test_data_complete.json
    """
    try:
        if no_cache:
            console.print("[yellow]Cache disabled for this execution[/yellow]")

        # Parse parameters
        try:
            parsed_params = parse_parameters(params or [])
        except ValueError as e:
            console.print(f"[red]Error: {e}[/red]")
            raise typer.Exit(1)

        # Expand batch combinations
        try:
            batch = expand_batch_params(parsed_params)
        except ValueError as e:
            console.print(f"[red]Error: {e}[/red]")
            raise typer.Exit(1)

        # --data is incompatible with batch mode
        if batch.is_batch and data is not None:
            console.print("[red]Error: --data cannot be used in batch mode.[/red]")
            raise typer.Exit(1)

        # --open is meaningless in batch mode
        if batch.is_batch and open_after:
            console.print("[yellow]Warning: --open is ignored in batch mode.[/yellow]")
            open_after = False

        # Get report definition (validate once, shared across all combos)
        from schoolreport.services.registry import ReportNotFoundError

        try:
            registry = get_registry()
            report = registry.get(report_id)
        except ReportNotFoundError:
            console.print(f"[red]Error: Report '{report_id}' not found.[/red]")
            console.print("Use 'schoolreport reports list' to see available reports.")
            raise typer.Exit(1)

        # Validate required parameters (all combos share the same keys)
        for param in report.parameters:
            if param.required and param.name not in batch.combinations[0]:
                console.print(f"[red]Error: Required parameter missing: {param.name}[/red]")
                console.print(f"\nRequired parameters for {report_id}:")
                for p in report.parameters:
                    if p.required:
                        console.print(f"  - {p.name}: {p.description or p.type.value}")
                raise typer.Exit(1)

        # Validate GCS configuration if upload requested
        if upload:
            try:
                from schoolreport.config import get_local_settings

                settings = get_local_settings()
                if not settings.gcs_bucket_name:
                    console.print("[red]Error: --upload requires GCS_BUCKET_NAME environment variable.[/red]")
                    console.print("\nTo upload to GCS, set the bucket name:")
                    console.print("  export GCS_BUCKET_NAME=your-bucket-name")
                    console.print("\nOr omit --upload to save locally only.")
                    raise typer.Exit(1)
            except Exception as e:
                if "GCS_BUCKET_NAME" in str(e):
                    raise
                pass

        # --- Single report ---
        if not batch.is_batch:
            resolved_output = output if output is not None else _default_output(report_id, parsed_params, data_only)
            _run_single_generate(
                report=report,
                report_id=report_id,
                parsed_params=parsed_params,
                output=resolved_output,
                data=data,
                data_only=data_only,
                upload=upload,
                open_after=open_after,
                keep_chart_files=keep_chart_files,
                no_cache=no_cache,
            )

        # --- Batch mode ---
        else:
            total = len(batch.combinations)
            console.print(f"[bold]Batch mode: {total} reports to generate[/bold]\n")
            successes: List = []
            failures: List = []

            for i, combo in enumerate(batch.combinations, start=1):
                label = f"[{i}/{total}]"
                resolved_output = _resolve_output_for_batch(output, report_id, combo, data_only)
                console.rule(f"{label} {report_id} — {combo}")
                try:
                    result_path = _run_single_generate(
                        report=report,
                        report_id=report_id,
                        parsed_params=combo,
                        output=resolved_output,
                        data=None,
                        data_only=data_only,
                        upload=upload,
                        open_after=False,
                        keep_chart_files=keep_chart_files,
                        no_cache=no_cache,
                        label=label,
                    )
                    successes.append((combo, result_path))
                except typer.Exit:
                    failures.append(combo)
                    console.print(f"[red]{label} FAILED — continuing with remaining reports...[/red]\n")

            # Summary
            console.rule("Batch Summary")
            console.print(f"[green]{len(successes)}/{total} succeeded[/green]")
            for combo, path in successes:
                console.print(f"  [green]✓[/green] {combo} → {path}")
            if failures:
                console.print(f"[red]{len(failures)}/{total} failed[/red]")
                for combo in failures:
                    console.print(f"  [red]✗[/red] {combo}")
                raise typer.Exit(1)

    except typer.Exit:
        raise
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)
