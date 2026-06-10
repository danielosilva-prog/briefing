"""PDF rendering service using Typst."""

import asyncio
import json
import logging
import tempfile
from pathlib import Path
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


class PDFRendererError(Exception):
    """Raised when PDF rendering fails."""

    pass


class PDFRenderer:
    """
    Render PDFs using Typst templating engine.

    Combines report data and charts into JSON, passes to Typst template,
    and compiles to PDF.
    """

    def __init__(self, typst_bin: str = "typst"):
        """
        Initialize PDF renderer.

        Args:
            typst_bin: Path to typst binary
        """
        self.typst_bin = typst_bin

    async def render(
        self,
        template_path: Path,
        output_path: Path,
        data: Dict[str, Any],
        assets_dir: Optional[Path] = None,
    ) -> Path:
        """
        Render a PDF from Typst template and data.

        Args:
            template_path: Path to Typst template file (.typ)
            output_path: Where to write the output PDF
            data: Report data (queries + charts)
            assets_dir: Optional assets directory for fonts/images

        Returns:
            Path to generated PDF

        Raises:
            PDFRendererError: If rendering fails
        """
        try:
            # Validate template exists
            if not template_path.exists():
                raise PDFRendererError(f"Template not found: {template_path}")

            # Prepare data JSON file
            temp_dir = Path(tempfile.mkdtemp())
            data_file = self._prepare_data(data, temp_dir)

            # Build typst command
            cmd = self._build_command(
                template_path=template_path,
                output_path=output_path,
                data_file=data_file,
                assets_dir=assets_dir
            )

            logger.info(f"Running Typst: {' '.join(str(c) for c in cmd)}")

            # Execute typst
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )

            stdout, stderr = await process.communicate()

            if process.returncode != 0:
                error_msg = stderr.decode() if stderr else "Unknown error"
                logger.error(f"Typst compilation failed: {error_msg}")
                raise PDFRendererError(f"Typst compilation failed: {error_msg}")

            # Verify output was created
            if not output_path.exists():
                raise PDFRendererError(f"PDF not generated at {output_path}")

            logger.info(f"PDF generated successfully: {output_path}")
            return output_path

        except PDFRendererError:
            raise
        except Exception as e:
            logger.error(f"PDF rendering failed: {e}")
            raise PDFRendererError(f"PDF rendering failed: {e}") from e

    def _prepare_data(self, data: Dict[str, Any], temp_dir: Path) -> Path:
        """
        Write data to JSON file for Typst input.

        Args:
            data: Data dictionary
            temp_dir: Temporary directory

        Returns:
            Path to JSON file
        """
        data_file = temp_dir / "data.json"

        with open(data_file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        return data_file

    def _build_command(
        self,
        template_path: Path,
        output_path: Path,
        data_file: Path,
        assets_dir: Optional[Path] = None,
    ) -> list[str]:
        """
        Build Typst command line.

        Args:
            template_path: Template file
            output_path: Output PDF path
            data_file: Data JSON file
            assets_dir: Optional assets directory

        Returns:
            Command as list of strings
        """
        cmd = [
            self.typst_bin,
            "compile",
            str(template_path),
            str(output_path),
            "--input",
            f"data={data_file}",
        ]

        # Add assets directory as root
        if assets_dir:
            cmd.extend(["--root", str(assets_dir)])

        return cmd
