"""Tests for executor pipeline service."""

import pytest
from pathlib import Path
from uuid import uuid4
from unittest.mock import AsyncMock, MagicMock, patch

import pandas as pd

from schoolreport.models.report import (
    ReportDefinition,
    Parameter,
    ParameterType,
    Query,
    Chart,
    ChartType,
    SourceType,
    Template,
    Cache,
    Sources,
    BigQuerySource,
)
from schoolreport.services.executor import ReportExecutor, ExecutorError
from schoolreport.services.registry import ReportRegistry, ReportNotFoundError


@pytest.fixture
def mock_registry():
    """Mock report registry."""
    registry = MagicMock(spec=ReportRegistry)
    return registry


@pytest.fixture
def mock_data_layer():
    """Mock data layer."""
    data_layer = AsyncMock()
    data_layer.execute_many = AsyncMock(return_value={
        "municipio": pd.DataFrame({"nome": ["Fortaleza"], "cod_ibge": ["2304400"]}),
        "matriculas": pd.DataFrame({"etapa": ["Fund I", "Fund II"], "total": [1000, 800]}),
    })
    return data_layer


@pytest.fixture
def mock_chart_generator():
    """Mock chart generator."""
    chart_gen = AsyncMock()
    chart_gen.generate_many = AsyncMock(return_value={
        "matriculas_bar": "base64_svg_content_here"
    })
    return chart_gen


@pytest.fixture
def mock_pdf_renderer():
    """Mock PDF renderer."""
    renderer = AsyncMock()
    renderer.render = AsyncMock()
    return renderer


@pytest.fixture
def mock_storage():
    """Mock GCS storage client."""
    storage = AsyncMock()
    storage.upload_file = AsyncMock(return_value="gs://bucket/reports/test.pdf")
    return storage


@pytest.fixture
def mock_cache():
    """Mock cache service."""
    cache = AsyncMock()
    cache.get = AsyncMock(return_value=None)  # Cache miss by default
    cache.set = AsyncMock()
    return cache


@pytest.fixture
def mock_audit():
    """Mock audit service."""
    audit = AsyncMock()
    audit.log_start = AsyncMock(return_value=uuid4())
    audit.log_complete = AsyncMock()
    audit.log_failure = AsyncMock()
    return audit


@pytest.fixture
def sample_report_def(tmp_path):
    """Create a sample report definition."""
    # Create query files
    queries_dir = tmp_path / "queries"
    queries_dir.mkdir()
    (queries_dir / "municipio.sql").write_text("SELECT * FROM municipios WHERE cod_ibge = @cod_ibge")
    (queries_dir / "matriculas.sql").write_text("SELECT * FROM matriculas WHERE cod_ibge = @cod_ibge")

    # Create template
    template_dir = tmp_path / "template"
    template_dir.mkdir()
    (template_dir / "main.typ").write_text("= Report\n#let data = json(sys.inputs.data)")

    report = ReportDefinition(
        id="TEST_REPORT",
        name="Test Report",
        description="A test report",
        version="1.0.0",
        parameters=[
            Parameter(name="cod_ibge", type=ParameterType.STRING, required=True, pattern="^[0-9]{7}$"),
            Parameter(name="ano", type=ParameterType.INTEGER, required=False, default=2024),
        ],
        sources=Sources(bigquery=BigQuerySource(project="test-project")),
        queries=[
            Query(name="municipio", source=SourceType.BIGQUERY, file="queries/municipio.sql"),
            Query(name="matriculas", source=SourceType.BIGQUERY, file="queries/matriculas.sql"),
        ],
        charts=[
            Chart(name="matriculas_bar", type=ChartType.BAR, data="matriculas", x="etapa", y="total"),
        ],
        template=Template(entry="template/main.typ", assets="template/assets"),
        cache=Cache(enabled=True, ttl_days=30),
    )
    report._report_dir = tmp_path
    return report


@pytest.fixture
def executor(
    mock_registry,
    mock_data_layer,
    mock_chart_generator,
    mock_pdf_renderer,
    mock_storage,
    mock_cache,
    mock_audit,
):
    """Create executor with all mocked dependencies."""
    return ReportExecutor(
        registry=mock_registry,
        data_layer=mock_data_layer,
        chart_generator=mock_chart_generator,
        pdf_renderer=mock_pdf_renderer,
        storage_client=mock_storage,
        cache_service=mock_cache,
        audit_service=mock_audit,
    )


class TestReportExecutor:
    """Test cases for ReportExecutor."""

    @pytest.mark.asyncio
    async def test_execute_full_pipeline(
        self,
        executor,
        mock_registry,
        mock_data_layer,
        mock_chart_generator,
        mock_pdf_renderer,
        mock_storage,
        mock_cache,
        mock_audit,
        sample_report_def,
        tmp_path,
    ):
        """Test full execution pipeline from start to finish."""
        mock_registry.get.return_value = sample_report_def

        # Setup PDF renderer to create output file
        async def mock_render(template_path, output_path, data, assets_dir=None):
            output_path.write_bytes(b"%PDF-1.4 test content")
            return output_path

        mock_pdf_renderer.render.side_effect = mock_render

        job_id = uuid4()
        params = {"cod_ibge": "2304400", "ano": 2024}

        result = await executor.execute(
            job_id=job_id,
            report_id="TEST_REPORT",
            parameters=params,
            requester="test_user",
        )

        # Verify result
        assert "gcs_path" in result
        assert "duration_ms" in result
        assert result["cached"] is False

        # Verify all stages were called
        mock_registry.get.assert_called_once_with("TEST_REPORT")
        mock_cache.get.assert_called_once()
        mock_data_layer.execute_many.assert_called_once()
        mock_chart_generator.generate_many.assert_called_once()
        mock_pdf_renderer.render.assert_called_once()
        mock_storage.upload_file.assert_called_once()
        mock_cache.set.assert_called_once()
        mock_audit.log_start.assert_called_once()
        mock_audit.log_complete.assert_called_once()

    @pytest.mark.asyncio
    async def test_execute_cache_hit(
        self,
        executor,
        mock_registry,
        mock_data_layer,
        mock_cache,
        mock_audit,
        sample_report_def,
    ):
        """Test that cache hit returns early without generating report."""
        mock_registry.get.return_value = sample_report_def
        mock_cache.get.return_value = "gs://bucket/cached/report.pdf"

        job_id = uuid4()
        params = {"cod_ibge": "2304400"}

        result = await executor.execute(
            job_id=job_id,
            report_id="TEST_REPORT",
            parameters=params,
        )

        # Should return cached path
        assert result["gcs_path"] == "gs://bucket/cached/report.pdf"
        assert result["cached"] is True

        # Should NOT call data layer or rendering
        mock_data_layer.execute_many.assert_not_called()
        mock_audit.log_complete.assert_called_once()

    @pytest.mark.asyncio
    async def test_execute_report_not_found(self, executor, mock_registry):
        """Test that missing report raises error."""
        mock_registry.get.side_effect = ReportNotFoundError("UNKNOWN")

        job_id = uuid4()

        with pytest.raises(ExecutorError, match="Report generation failed"):
            await executor.execute(
                job_id=job_id,
                report_id="UNKNOWN",
                parameters={},
            )

    @pytest.mark.asyncio
    async def test_execute_missing_required_parameter(
        self, executor, mock_registry, sample_report_def
    ):
        """Test that missing required parameter raises error."""
        mock_registry.get.return_value = sample_report_def

        job_id = uuid4()
        params = {}  # Missing required cod_ibge

        with pytest.raises(ExecutorError, match="Required parameter missing"):
            await executor.execute(
                job_id=job_id,
                report_id="TEST_REPORT",
                parameters=params,
            )

    @pytest.mark.asyncio
    async def test_execute_data_layer_failure(
        self,
        executor,
        mock_registry,
        mock_data_layer,
        mock_cache,
        mock_audit,
        sample_report_def,
    ):
        """Test that data layer failures are logged and propagated."""
        mock_registry.get.return_value = sample_report_def
        mock_data_layer.execute_many.side_effect = Exception("BigQuery timeout")

        job_id = uuid4()
        params = {"cod_ibge": "2304400"}

        with pytest.raises(ExecutorError, match="Report generation failed"):
            await executor.execute(
                job_id=job_id,
                report_id="TEST_REPORT",
                parameters=params,
            )

        # Should log failure
        mock_audit.log_failure.assert_called_once()

    @pytest.mark.asyncio
    async def test_execute_chart_generation_failure(
        self,
        executor,
        mock_registry,
        mock_data_layer,
        mock_chart_generator,
        mock_cache,
        mock_audit,
        sample_report_def,
    ):
        """Test that chart generation failures are handled."""
        mock_registry.get.return_value = sample_report_def
        mock_chart_generator.generate_many.side_effect = Exception("Chart error")

        job_id = uuid4()
        params = {"cod_ibge": "2304400"}

        with pytest.raises(ExecutorError):
            await executor.execute(
                job_id=job_id,
                report_id="TEST_REPORT",
                parameters=params,
            )

        mock_audit.log_failure.assert_called_once()

    @pytest.mark.asyncio
    async def test_execute_pdf_render_failure(
        self,
        executor,
        mock_registry,
        mock_data_layer,
        mock_chart_generator,
        mock_pdf_renderer,
        mock_cache,
        mock_audit,
        sample_report_def,
    ):
        """Test that PDF rendering failures are handled."""
        mock_registry.get.return_value = sample_report_def
        mock_pdf_renderer.render.side_effect = Exception("Typst compilation failed")

        job_id = uuid4()
        params = {"cod_ibge": "2304400"}

        with pytest.raises(ExecutorError):
            await executor.execute(
                job_id=job_id,
                report_id="TEST_REPORT",
                parameters=params,
            )

        mock_audit.log_failure.assert_called_once()

    @pytest.mark.asyncio
    async def test_execute_storage_upload_failure(
        self,
        executor,
        mock_registry,
        mock_data_layer,
        mock_chart_generator,
        mock_pdf_renderer,
        mock_storage,
        mock_cache,
        mock_audit,
        sample_report_def,
        tmp_path,
    ):
        """Test that storage upload failures are handled."""
        mock_registry.get.return_value = sample_report_def

        async def mock_render(template_path, output_path, data, assets_dir=None):
            output_path.write_bytes(b"%PDF-1.4 test")
            return output_path

        mock_pdf_renderer.render.side_effect = mock_render
        mock_storage.upload_file.side_effect = Exception("GCS upload failed")

        job_id = uuid4()
        params = {"cod_ibge": "2304400"}

        with pytest.raises(ExecutorError):
            await executor.execute(
                job_id=job_id,
                report_id="TEST_REPORT",
                parameters=params,
            )

        mock_audit.log_failure.assert_called_once()

    @pytest.mark.asyncio
    async def test_execute_no_charts(
        self,
        executor,
        mock_registry,
        mock_data_layer,
        mock_chart_generator,
        mock_pdf_renderer,
        mock_storage,
        mock_cache,
        mock_audit,
        tmp_path,
    ):
        """Test report with no charts defined."""
        # Create report without charts
        report = ReportDefinition(
            id="NO_CHARTS",
            name="No Charts Report",
            parameters=[],
            queries=[
                Query(name="data", source=SourceType.BIGQUERY, file="queries/data.sql"),
            ],
            charts=[],  # No charts
            template=Template(entry="template/main.typ"),
        )

        queries_dir = tmp_path / "queries"
        queries_dir.mkdir()
        (queries_dir / "data.sql").write_text("SELECT 1")

        template_dir = tmp_path / "template"
        template_dir.mkdir()
        (template_dir / "main.typ").write_text("= Report")

        report._report_dir = tmp_path
        mock_registry.get.return_value = report

        mock_data_layer.execute_many.return_value = {
            "data": pd.DataFrame({"x": [1]})
        }

        async def mock_render(template_path, output_path, data, assets_dir=None):
            output_path.write_bytes(b"%PDF")
            return output_path

        mock_pdf_renderer.render.side_effect = mock_render

        job_id = uuid4()

        result = await executor.execute(
            job_id=job_id,
            report_id="NO_CHARTS",
            parameters={},
        )

        # Should still work - executor returns early with empty dict when no charts
        assert result["cached"] is False
        # Chart generator is NOT called when charts list is empty (early return in _generate_charts)
        mock_chart_generator.generate_many.assert_not_called()

    @pytest.mark.asyncio
    async def test_execute_duration_tracking(
        self,
        executor,
        mock_registry,
        mock_data_layer,
        mock_pdf_renderer,
        mock_storage,
        mock_cache,
        mock_audit,
        sample_report_def,
    ):
        """Test that duration is tracked correctly."""
        mock_registry.get.return_value = sample_report_def

        async def mock_render(template_path, output_path, data, assets_dir=None):
            output_path.write_bytes(b"%PDF")
            return output_path

        mock_pdf_renderer.render.side_effect = mock_render

        job_id = uuid4()
        params = {"cod_ibge": "2304400"}

        result = await executor.execute(
            job_id=job_id,
            report_id="TEST_REPORT",
            parameters=params,
        )

        # Duration should be positive integer
        assert isinstance(result["duration_ms"], int)
        assert result["duration_ms"] >= 0

        # Audit should receive duration
        call_args = mock_audit.log_complete.call_args
        assert call_args[0][2] == result["duration_ms"]  # duration_ms argument


class TestParameterValidation:
    """Test cases for parameter validation."""

    def test_validate_required_parameter_present(self, executor, sample_report_def):
        """Test validation passes when required parameter is present."""
        params = {"cod_ibge": "2304400"}

        # Should not raise
        executor._validate_parameters(sample_report_def, params)

    def test_validate_required_parameter_missing(self, executor, sample_report_def):
        """Test validation fails when required parameter is missing."""
        params = {}  # Missing cod_ibge

        with pytest.raises(ExecutorError, match="Required parameter missing: cod_ibge"):
            executor._validate_parameters(sample_report_def, params)

    def test_validate_optional_parameter_missing(self, executor, sample_report_def):
        """Test validation passes when optional parameter is missing."""
        params = {"cod_ibge": "2304400"}  # ano is optional

        # Should not raise
        executor._validate_parameters(sample_report_def, params)

    def test_validate_extra_parameters_allowed(self, executor, sample_report_def):
        """Test that extra parameters are allowed (ignored)."""
        params = {
            "cod_ibge": "2304400",
            "extra_param": "ignored",
        }

        # Should not raise
        executor._validate_parameters(sample_report_def, params)
