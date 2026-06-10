"""Report definition models."""

from enum import Enum
from pathlib import Path
from typing import Any, Literal, Optional

from pydantic import BaseModel, Field, field_validator


class ParameterType(str, Enum):
    """Parameter types for report definitions."""

    STRING = "string"
    INTEGER = "integer"
    NUMBER = "number"
    BOOLEAN = "boolean"
    ARRAY = "array"
    DATE = "date"


class Parameter(BaseModel):
    """A report parameter definition."""

    name: str = Field(..., description="Parameter name")
    type: ParameterType = Field(..., description="Parameter type")
    required: bool = Field(default=True, description="Whether parameter is required")
    description: Optional[str] = Field(None, description="Parameter description")
    default: Optional[Any] = Field(None, description="Default value")

    # Validation constraints
    pattern: Optional[str] = Field(None, description="Regex pattern for string types")
    min_length: Optional[int] = Field(None, description="Min length for strings")
    max_length: Optional[int] = Field(None, description="Max length for strings")
    min: Optional[float] = Field(None, description="Min value for numbers")
    max: Optional[float] = Field(None, description="Max value for numbers")

    # Array constraints
    items: Optional[ParameterType] = Field(None, description="Type of array items")
    min_items: Optional[int] = Field(None, description="Min array length")
    max_items: Optional[int] = Field(None, description="Max array length")


class SourceType(str, Enum):
    """Data source types."""

    BIGQUERY = "bigquery"
    POSTGRES = "postgres"


class BigQuerySource(BaseModel):
    """BigQuery source configuration."""

    project: str = Field(..., description="GCP project ID")
    dataset: Optional[str] = Field(None, description="Default dataset")


class PostgresSource(BaseModel):
    """PostgreSQL source configuration."""

    connection: str = Field(default="default", description="Connection name")


class Sources(BaseModel):
    """Data sources configuration."""

    bigquery: Optional[BigQuerySource] = None
    postgres: Optional[PostgresSource] = None


class Query(BaseModel):
    """A query definition."""

    name: str = Field(..., description="Query identifier")
    source: SourceType = Field(..., description="Data source type")
    file: str = Field(..., description="SQL file path relative to report directory")


class ChartType(str, Enum):
    """Chart types."""

    BAR = "bar"
    DONUT = "donut"
    LINE = "line"
    STACKED_BAR = "stacked_bar"
    MAP = "map"


class Chart(BaseModel):
    """A chart definition."""

    name: str = Field(..., description="Chart identifier")
    type: ChartType = Field(..., description="Chart type")
    data: str = Field(..., description="Query name to use for data")

    # Common fields
    title: Optional[str] = Field(None, description="Chart title")
    color: Optional[str] = Field(None, description="Primary color")
    colors: Optional[list[str]] = Field(None, description="Color palette")

    # Bar/Line chart fields
    x: Optional[str] = Field(None, description="X-axis column")
    y: Optional[str] = Field(None, description="Y-axis column")

    # Donut chart fields
    values: Optional[str] = Field(None, description="Values column")
    labels: Optional[str] = Field(None, description="Labels column")

    # Stacked bar fields
    stack: Optional[str] = Field(None, description="Stack grouping column")

    # Map fields
    geo_column: Optional[str] = Field(None, description="Geographic column")


class Template(BaseModel):
    """Template configuration."""

    entry: str = Field(..., description="Entry template file (e.g., template/main.typ)")
    assets: Optional[str] = Field(None, description="Assets directory path")


class Cache(BaseModel):
    """Cache configuration."""

    enabled: bool = Field(default=True, description="Enable caching")
    ttl_days: int = Field(default=30, description="Cache TTL in days")


class ReportDefinition(BaseModel):
    """Complete report definition from report.yaml."""

    id: str = Field(..., description="Unique report identifier")
    name: str = Field(..., description="Human-readable report name")
    description: Optional[str] = Field(None, description="Report description")
    version: str = Field(default="1.0.0", description="Report version")

    parameters: list[Parameter] = Field(default_factory=list, description="Report parameters")
    sources: Sources = Field(default_factory=Sources, description="Data sources")
    queries: list[Query] = Field(default_factory=list, description="Queries to execute")
    charts: list[Chart] = Field(default_factory=list, description="Charts to generate")
    template: Template = Field(..., description="Template configuration")
    cache: Cache = Field(default_factory=Cache, description="Cache configuration")

    # Internal fields (set by registry)
    _report_dir: Optional[Path] = None

    @field_validator("id")
    @classmethod
    def validate_id(cls, v: str) -> str:
        """Validate report ID is uppercase alphanumeric."""
        if not v.isupper():
            raise ValueError(f"Report ID must be uppercase: {v}")
        if not v.replace("_", "").replace("-", "").isalnum():
            raise ValueError(f"Report ID must be alphanumeric (underscores/hyphens allowed): {v}")
        return v

    def get_query_path(self, query: Query) -> Path:
        """Get absolute path to query SQL file."""
        if self._report_dir is None:
            raise ValueError("Report directory not set")
        return self._report_dir / query.file

    def get_template_path(self) -> Path:
        """Get absolute path to template entry file."""
        if self._report_dir is None:
            raise ValueError("Report directory not set")
        return self._report_dir / self.template.entry

    def get_assets_path(self) -> Optional[Path]:
        """Get absolute path to assets directory."""
        if self._report_dir is None or self.template.assets is None:
            return None
        return self._report_dir / self.template.assets
