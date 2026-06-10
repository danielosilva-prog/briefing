"""Typst CLI wrapper for PDF generation."""

import asyncio
import json
import logging
import math
from numbers import Real
import subprocess
import uuid
from typing import Optional, Dict, Any
from pathlib import Path

logger = logging.getLogger(__name__)


def _json_safe(value: Any) -> Any:
    """Convert non-JSON values (NaN/Inf) to JSON-safe equivalents."""
    if isinstance(value, dict):
        return {k: _json_safe(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_json_safe(v) for v in value]
    if isinstance(value, tuple):
        return [_json_safe(v) for v in value]
    if isinstance(value, Real) and not isinstance(value, bool):
        num = float(value)
        if math.isnan(num) or math.isinf(num):
            return None
    return value


class TypstError(Exception):
    """Raised when Typst operation fails."""

    pass


class TypstClient:
    """Wrapper for Typst CLI commands."""

    def __init__(self, typst_bin: str = "typst"):
        """Initialize Typst client.

        Args:
            typst_bin: Path to typst binary (default: "typst" from PATH)
        """
        self.typst_bin = typst_bin

    async def get_version(self) -> str:
        """Get Typst version.

        Returns:
            Version string

        Raises:
            TypstError: If version check fails
        """
        try:
            proc = await asyncio.create_subprocess_exec(
                self.typst_bin,
                "--version",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )

            stdout, stderr = await proc.communicate()

            if proc.returncode != 0:
                raise TypstError(f"Version check failed: {stderr.decode()}")

            return stdout.decode().strip()
        except FileNotFoundError:
            raise TypstError(f"Typst binary not found: {self.typst_bin}")
        except Exception as e:
            raise TypstError(f"Version check failed: {e}")

    async def compile(
        self,
        template_path: Path,
        output_path: Path,
        root: Optional[Path] = None,
        inputs: Optional[Dict[str, str]] = None,
        font_paths: Optional[list[Path]] = None
    ) -> bytes:
        """Compile Typst template to PDF.

        Args:
            template_path: Path to .typ template file
            output_path: Path where PDF should be saved
            root: Optional root directory for template
            inputs: Optional dictionary of input variables (--input key=value)
            font_paths: Optional list of font directories

        Returns:
            PDF content as bytes

        Raises:
            TypstError: If compilation fails
        """
        cmd = [self.typst_bin, "compile"]

        # Add root if specified
        if root:
            cmd.extend(["--root", str(root)])

        # Add inputs if specified
        if inputs:
            for key, value in inputs.items():
                cmd.extend(["--input", f"{key}={value}"])

        # Add font paths if specified
        if font_paths:
            for font_path in font_paths:
                cmd.extend(["--font-path", str(font_path)])

        # Add template and output paths
        cmd.extend([str(template_path), str(output_path)])

        try:
            proc = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )

            stdout, stderr = await proc.communicate()

            if proc.returncode != 0:
                error_msg = stderr.decode() if stderr else "Unknown error"
                raise TypstError(f"Compilation failed: {error_msg}")

            # Read the generated PDF
            if not output_path.exists():
                raise TypstError(f"Output file not created: {output_path}")

            with open(output_path, "rb") as f:
                pdf_content = f.read()

            return pdf_content

        except FileNotFoundError:
            raise TypstError(f"Typst binary not found: {self.typst_bin}")
        except TypstError:
            raise
        except Exception as e:
            raise TypstError(f"Compilation failed: {e}")

    async def query(
        self,
        template_path: Path,
        selector: str,
        root: Optional[Path] = None
    ) -> str:
        """Query template for information.

        Args:
            template_path: Path to .typ template file
            selector: Query selector
            root: Optional root directory for template

        Returns:
            Query result as string

        Raises:
            TypstError: If query fails
        """
        cmd = [self.typst_bin, "query", str(template_path), selector]

        if root:
            cmd.extend(["--root", str(root)])

        try:
            proc = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )

            stdout, stderr = await proc.communicate()

            if proc.returncode != 0:
                error_msg = stderr.decode() if stderr else "Unknown error"
                raise TypstError(f"Query failed: {error_msg}")

            return stdout.decode().strip()

        except FileNotFoundError:
            raise TypstError(f"Typst binary not found: {self.typst_bin}")
        except TypstError:
            raise
        except Exception as e:
            raise TypstError(f"Query failed: {e}")

    async def check(self, template_path: Path, root: Optional[Path] = None) -> bool:
        """Check template for errors without compiling.

        Args:
            template_path: Path to .typ template file
            root: Optional root directory for template

        Returns:
            True if template is valid, False otherwise
        """
        try:
            cmd = [self.typst_bin, "compile", "--dry-run", str(template_path)]

            if root:
                cmd.extend(["--root", str(root)])

            proc = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )

            await proc.communicate()

            return proc.returncode == 0

        except Exception:
            return False

    async def is_available(self) -> bool:
        """Check if Typst is available.

        Returns:
            True if Typst is available, False otherwise
        """
        try:
            await self.get_version()
            return True
        except TypstError:
            return False

    async def render_to_bytes(
        self,
        template_path: Path,
        data: Dict[str, Any],
        *,
        input_key: str = "data_file",
    ) -> bytes:
        """Render a Typst template to PDF bytes (via stdout).

        Writes *data* to a temporary JSON file inside the template directory
        (required by Typst's ``--root`` restriction) and compiles directly to
        stdout, avoiding the need for an intermediate output file.

        Args:
            template_path: Path to the ``.typ`` entry file.
            data: Data dict to pass to the template as JSON.
            input_key: Typst ``--input`` key name for the data file.

        Returns:
            Raw PDF bytes.

        Raises:
            TypstError: If compilation fails.
        """
        root = template_path.parent
        data_filename = f".data_{uuid.uuid4().hex[:8]}.json"
        data_path = root / data_filename

        try:
            safe_data = _json_safe(data)
            with open(data_path, "w", encoding="utf-8") as f:
                json.dump(safe_data, f, ensure_ascii=False, default=str, allow_nan=False)

            cmd = [
                self.typst_bin,
                "compile",
                str(template_path),
                "-",  # output to stdout
                "--root",
                str(root),
                "--input",
                f"{input_key}={data_filename}",
            ]

            proc = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, stderr = await proc.communicate()

            if proc.returncode != 0:
                error_msg = stderr.decode("utf-8")
                logger.error(f"Typst compilation failed: {error_msg}")
                raise TypstError(f"Compilation failed: {error_msg}")

            return stdout
        finally:
            data_path.unlink(missing_ok=True)

    async def render(
        self,
        template_path: Path,
        output_path: Path,
        data: Dict[str, Any],
        assets_dir: Optional[Path] = None,
        keep_chart_files: bool = False,
    ) -> Path:
        """
        High-level render method for PDF generation.

        Args:
            template_path: Path to .typ template
            output_path: Path for output PDF
            data: Data to pass to template as JSON input (charts should be base64-encoded SVGs)
            assets_dir: Optional assets directory
            keep_chart_files: When True, preserves temporary .chart_*.svg and .data_*.json files

        Returns:
            Path to generated PDF
        """
        import base64

        # Determine root directory
        root = template_path.parent

        # Track temp files for cleanup
        temp_files: list[Path] = []

        try:
            # Process charts: decode base64 SVGs and save as files
            # Replace base64 content with file paths in data
            if "charts" in data and data["charts"]:
                chart_paths = {}
                for chart_name, chart_b64 in data["charts"].items():
                    # Decode base64 to raw SVG
                    try:
                        svg_bytes = base64.b64decode(chart_b64)
                    except Exception:
                        # If not valid base64, skip
                        continue

                    # Save to temp file in template directory
                    chart_filename = f".chart_{chart_name}_{uuid.uuid4().hex[:8]}.svg"
                    chart_path = root / chart_filename
                    chart_path.write_bytes(svg_bytes)
                    temp_files.append(chart_path)

                    # Store relative path for template
                    chart_paths[chart_name] = chart_filename

                # Update data with file paths
                data = dict(data)  # Copy to avoid mutating original
                data["charts"] = chart_paths

            # Write data to temp JSON file WITHIN the template directory
            # This is required because Typst's --root restricts file access
            data_filename = f".data_{uuid.uuid4().hex[:8]}.json"
            data_path = root / data_filename
            temp_files.append(data_path)

            safe_data = _json_safe(data)
            with open(data_path, 'w', encoding='utf-8') as f:
                json.dump(safe_data, f, ensure_ascii=False, default=str, allow_nan=False)

            # Prepare inputs - use relative path from root
            inputs = {"data": data_filename}

            # Compile
            await self.compile(
                template_path=template_path,
                output_path=output_path,
                root=root,
                inputs=inputs,
            )

            return output_path
        finally:
            if not keep_chart_files:
                # Clean up all temp files
                for temp_file in temp_files:
                    temp_file.unlink(missing_ok=True)


# Alias for compatibility
TypstRenderer = TypstClient
