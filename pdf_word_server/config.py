from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_TEMP_ROOT = PROJECT_ROOT / "work"


@dataclass(frozen=True)
class Settings:
    host: str
    port: int
    converter_engine: str
    upload_limit_mb: int
    word_timeout_seconds: int
    temp_root: Path


def get_settings() -> Settings:
    return Settings(
        host=os.getenv("HOST", "0.0.0.0"),
        port=int(os.getenv("PORT", "8080")),
        converter_engine=os.getenv("CONVERTER_ENGINE", "pdf2docx").strip().lower(),
        upload_limit_mb=int(os.getenv("MAX_UPLOAD_MB", "100")),
        word_timeout_seconds=int(os.getenv("WORD_TIMEOUT_SECONDS", "300")),
        temp_root=Path(os.getenv("TEMP_ROOT", DEFAULT_TEMP_ROOT)).resolve(),
    )
