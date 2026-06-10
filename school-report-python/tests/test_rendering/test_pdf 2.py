"""Tests for PDF rendering service."""

import pytest
import json
from pathlib import Path
from unittest.mock import AsyncMock, patch, MagicMock

from schoolreport.rendering.pdf import PDFRenderer, PDFRendererError


@pytest.fixture
def pdf_renderer():
    """Create PDFRenderer instance."""
    return PDFRenderer()


@pytest.fixture
def sample_data():
    """Sample report data."""
    return {
        "municipio": {
            "cod_ibge": "2304400",
            "nome": "Fortaleza",
            "populacao": 2643247
        },
        "charts": {
            "matriculas_bar": "PHN2ZyB3aWR0aD0iODAwIiBoZWlnaHQ9IjYwMCI+PC9zdmc+",  # base64 SVG
        }
    }


class TestPDFRenderer:
    """Test cases for PDFRenderer."""

    @pytest.mark.asyncio
    async def test_render_pdf_success(self, pdf_renderer, sample_data, tmp_path):
        """Test successful PDF rendering."""
        template_path = tmp_path / "template.typ"
        template_path.write_text("#set document(title: \"Test\")\n= Test Report")

        # Mock typst subprocess
        with patch("schoolreport.rendering.pdf.asyncio.create_subprocess_exec") as mock_exec:
            # Mock successful process
            mock_process = AsyncMock()
            mock_process.returncode = 0
            mock_process.communicate = AsyncMock(return_value=(b"", b""))
            mock_exec.return_value = mock_process

            # Create a fake PDF file
            output_pdf = tmp_path / "output.pdf"
            output_pdf.write_bytes(b"%PDF-1.4 fake pdf content")

            result = await pdf_renderer.render(
                template_path=template_path,
                output_path=output_pdf,
                data=sample_data
            )

            assert result == output_pdf
            assert output_pdf.exists()
            assert output_pdf.stat().st_size > 0

    @pytest.mark.asyncio
    async def test_render_pdf_template_not_found(self, pdf_renderer, sample_data, tmp_path):
        """Test that missing template raises error."""
        template_path = tmp_path / "nonexistent.typ"
        output_path = tmp_path / "output.pdf"

        with pytest.raises(PDFRendererError, match="Template not found"):
            await pdf_renderer.render(template_path, output_path, sample_data)

    @pytest.mark.asyncio
    async def test_render_pdf_typst_failure(self, pdf_renderer, sample_data, tmp_path):
        """Test that Typst compilation errors are caught."""
        template_path = tmp_path / "template.typ"
        template_path.write_text("#invalid typst syntax")

        output_path = tmp_path / "output.pdf"

        # Mock typst subprocess with failure
        with patch("schoolreport.rendering.pdf.asyncio.create_subprocess_exec") as mock_exec:
            mock_process = AsyncMock()
            mock_process.returncode = 1
            mock_process.communicate = AsyncMock(return_value=(b"", b"Compilation error"))
            mock_exec.return_value = mock_process

            with pytest.raises(PDFRendererError, match="Typst compilation failed"):
                await pdf_renderer.render(template_path, output_path, sample_data)

    def test_prepare_data_json(self, pdf_renderer, sample_data, tmp_path):
        """Test data preparation to JSON file."""
        data_file = pdf_renderer._prepare_data(sample_data, tmp_path)

        assert data_file.exists()
        assert data_file.suffix == ".json"

        # Verify JSON content
        with open(data_file) as f:
            loaded_data = json.load(f)

        assert loaded_data == sample_data

    @pytest.mark.asyncio
    async def test_render_with_assets_directory(self, pdf_renderer, sample_data, tmp_path):
        """Test rendering with assets directory."""
        template_path = tmp_path / "template.typ"
        template_path.write_text("= Test")

        assets_dir = tmp_path / "assets"
        assets_dir.mkdir()
        (assets_dir / "logo.png").write_bytes(b"fake image")

        output_path = tmp_path / "output.pdf"

        with patch("schoolreport.rendering.pdf.asyncio.create_subprocess_exec") as mock_exec:
            mock_process = AsyncMock()
            mock_process.returncode = 0
            mock_process.communicate = AsyncMock(return_value=(b"", b""))
            mock_exec.return_value = mock_process

            output_path.write_bytes(b"%PDF-1.4")

            result = await pdf_renderer.render(
                template_path=template_path,
                output_path=output_path,
                data=sample_data,
                assets_dir=assets_dir
            )

            # Verify assets_dir was used in command
            call_args = mock_exec.call_args[0]
            assert any("--root" in str(arg) or str(assets_dir) in str(arg) for arg in call_args)

    def test_data_with_special_characters(self, pdf_renderer, tmp_path):
        """Test that special characters in data are properly escaped."""
        data = {
            "text": "Text with 'quotes' and \"double quotes\"",
            "unicode": "Município São José"
        }

        data_file = pdf_renderer._prepare_data(data, tmp_path)

        with open(data_file) as f:
            loaded = json.load(f)

        assert loaded["text"] == data["text"]
        assert loaded["unicode"] == data["unicode"]
