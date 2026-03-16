from __future__ import annotations

import subprocess
import threading
from pathlib import Path

from pdf2docx import Converter as Pdf2DocxEngine

from .config import PROJECT_ROOT

POWERSHELL_SCRIPT = PROJECT_ROOT / "scripts" / "convert_pdf_to_docx.ps1"


class ConversionError(RuntimeError):
    pass


class Pdf2DocxConverter:
    def __init__(self) -> None:
        self._lock = threading.Lock()

    def convert(self, input_path: Path, output_path: Path) -> None:
        try:
            with self._lock:
                converter = Pdf2DocxEngine(str(input_path))
                try:
                    converter.convert(str(output_path))
                finally:
                    converter.close()
        except Exception as exc:
            raise ConversionError(f"pdf2docx failed: {exc}") from exc

        if not output_path.exists() or output_path.stat().st_size == 0:
            raise ConversionError("pdf2docx did not generate a DOCX file.")


class WordPdfConverter:
    def __init__(self, timeout_seconds: int) -> None:
        self.timeout_seconds = timeout_seconds
        self._lock = threading.Lock()

    def convert(self, input_path: Path, output_path: Path) -> None:
        if not POWERSHELL_SCRIPT.exists():
            raise ConversionError(f"Missing conversion script: {POWERSHELL_SCRIPT}")

        command = [
            "powershell.exe",
            "-NoProfile",
            "-NonInteractive",
            "-ExecutionPolicy",
            "Bypass",
            "-File",
            str(POWERSHELL_SCRIPT),
            "-InputPath",
            str(input_path),
            "-OutputPath",
            str(output_path),
        ]

        try:
            with self._lock:
                result = subprocess.run(
                    command,
                    capture_output=True,
                    text=True,
                    timeout=self.timeout_seconds,
                    check=False,
                )
        except subprocess.TimeoutExpired as exc:
            raise ConversionError(
                f"Conversion timed out after {self.timeout_seconds} seconds."
            ) from exc

        if result.returncode != 0:
            details = "\n".join(
                chunk.strip() for chunk in (result.stdout, result.stderr) if chunk.strip()
            )
            raise ConversionError(details or "Microsoft Word failed to convert the PDF.")

        if not output_path.exists() or output_path.stat().st_size == 0:
            raise ConversionError("Microsoft Word did not generate a DOCX file.")


def build_converter(engine: str, timeout_seconds: int):
    normalized_engine = engine.strip().lower()
    if normalized_engine == "pdf2docx":
        return Pdf2DocxConverter()
    if normalized_engine == "word":
        return WordPdfConverter(timeout_seconds=timeout_seconds)

    raise ValueError(
        "Unsupported converter engine. Use 'pdf2docx' or 'word'."
    )
