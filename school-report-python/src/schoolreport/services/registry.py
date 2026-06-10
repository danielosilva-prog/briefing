"""Report registry service for discovering and managing report definitions."""

import logging
from pathlib import Path
from typing import Dict, List, Optional

import yaml
from pydantic import ValidationError

from schoolreport.models.report import ReportDefinition
from schoolreport.rendering.chart_framework import ChartLoader, ChartRegistry

logger = logging.getLogger(__name__)


class ReportNotFoundError(Exception):
    """Raised when a report is not found in the registry."""

    def __init__(self, report_id: str):
        self.report_id = report_id
        super().__init__(f"Report not found: {report_id}")


class ReportRegistry:
    """
    Registry for discovering and loading report definitions.

    Discovers report.yaml files in a reports directory and provides
    access to parsed ReportDefinition objects.
    """

    def __init__(self, reports_dir: Path | str):
        """
        Initialize the registry.

        Args:
            reports_dir: Directory containing report subdirectories
        """
        self.reports_dir = Path(reports_dir)
        self._reports: Dict[str, ReportDefinition] = {}
        self._chart_loader = ChartLoader()
        self._chart_registries: Dict[str, ChartRegistry] = {}
        self._load_reports()

    def _load_reports(self) -> None:
        """
        Discover and load all report definitions from the reports directory.

        Scans for subdirectories containing report.yaml files and loads them.
        """
        if not self.reports_dir.exists():
            logger.warning(f"Reports directory not found: {self.reports_dir}")
            return

        logger.info(f"Discovering reports in: {self.reports_dir}")

        for report_dir in self.reports_dir.iterdir():
            if not report_dir.is_dir():
                continue

            yaml_path = report_dir / "report.yaml"
            if not yaml_path.exists():
                logger.debug(f"Skipping {report_dir.name}: no report.yaml found")
                continue

            try:
                report = self._load_report(report_dir, yaml_path)
                self._reports[report.id] = report
                logger.info(f"Loaded report: {report.id} ({report.name})")

                # Load custom charts if charts.py exists
                chart_registry = self._chart_loader.load(report_dir, report.id)
                self._chart_registries[report.id] = chart_registry
            except Exception as e:
                logger.error(f"Failed to load report from {report_dir}: {e}")

        logger.info(f"Loaded {len(self._reports)} report(s)")

    def _load_report(self, report_dir: Path, yaml_path: Path) -> ReportDefinition:
        """
        Load a single report definition from YAML.

        Args:
            report_dir: Directory containing the report
            yaml_path: Path to report.yaml file

        Returns:
            Parsed ReportDefinition

        Raises:
            ValidationError: If YAML is invalid
            FileNotFoundError: If YAML file doesn't exist
        """
        with open(yaml_path, "r") as f:
            data = yaml.safe_load(f)

        # Parse with Pydantic
        report = ReportDefinition(**data)

        # Set internal report directory reference
        report._report_dir = report_dir

        return report

    def get(self, report_id: str) -> ReportDefinition:
        """
        Get a report definition by ID.

        Args:
            report_id: Report identifier

        Returns:
            ReportDefinition for the requested report

        Raises:
            ReportNotFoundError: If report doesn't exist
        """
        if report_id not in self._reports:
            raise ReportNotFoundError(report_id)

        return self._reports[report_id]

    def get_many(self, report_ids: List[str]) -> List[ReportDefinition]:
        """
        Get multiple report definitions by IDs.

        Args:
            report_ids: List of report identifiers

        Returns:
            List of ReportDefinitions in the same order as input

        Raises:
            ReportNotFoundError: If any report doesn't exist
        """
        reports = []
        for report_id in report_ids:
            if report_id not in self._reports:
                raise ReportNotFoundError(report_id)
            reports.append(self._reports[report_id])
        return reports

    def list(self) -> List[str]:
        """
        List all available report IDs.

        Returns:
            Sorted list of report IDs
        """
        return sorted(self._reports.keys())

    def exists(self, report_id: str) -> bool:
        """
        Check if a report exists.

        Args:
            report_id: Report identifier

        Returns:
            True if report exists, False otherwise
        """
        return report_id in self._reports

    def get_chart_registry(self, report_id: str) -> Optional[ChartRegistry]:
        """
        Get the chart registry for a report.

        Args:
            report_id: Report identifier

        Returns:
            ChartRegistry if report exists, None otherwise
        """
        return self._chart_registries.get(report_id)

    def reload(self) -> None:
        """
        Reload all report definitions from disk.

        Useful for development mode with hot reload.
        """
        logger.info("Reloading report definitions")
        self._reports.clear()
        self._chart_registries.clear()
        self._chart_loader = ChartLoader()
        self._load_reports()

    def get_all(self) -> Dict[str, ReportDefinition]:
        """
        Get all report definitions.

        Returns:
            Dictionary mapping report IDs to ReportDefinitions
        """
        return self._reports.copy()


# Global registry instance (can be initialized once at app startup)
_registry: ReportRegistry | None = None


def init_registry(reports_dir: Path | str) -> ReportRegistry:
    """
    Initialize the global registry instance.

    Args:
        reports_dir: Directory containing report subdirectories

    Returns:
        Initialized ReportRegistry
    """
    global _registry
    _registry = ReportRegistry(reports_dir)
    return _registry


def get_registry() -> ReportRegistry:
    """
    Get the global registry instance.

    Returns:
        The global ReportRegistry

    Raises:
        RuntimeError: If registry hasn't been initialized
    """
    if _registry is None:
        raise RuntimeError("Registry not initialized. Call init_registry() first.")
    return _registry
