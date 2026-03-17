from __future__ import annotations

import shutil
import tempfile
from pathlib import Path

from flask import Flask, current_app, jsonify, render_template, request, send_file
from werkzeug.exceptions import RequestEntityTooLarge
from werkzeug.utils import secure_filename

from .config import Settings, get_settings
from .conversion import ConversionError, build_converter

DOCX_MIMETYPE = (
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
)


def create_app(settings: Settings | None = None) -> Flask:
    app = Flask(__name__, template_folder="templates", static_folder="static")
    app.json.ensure_ascii = False

    resolved_settings = settings or get_settings()
    resolved_settings.temp_root.mkdir(parents=True, exist_ok=True)

    app.config["MAX_CONTENT_LENGTH"] = resolved_settings.upload_limit_mb * 1024 * 1024
    app.config["settings"] = resolved_settings
    app.config["converter"] = build_converter(
        engine=resolved_settings.converter_engine,
        timeout_seconds=resolved_settings.word_timeout_seconds,
    )

    @app.get("/")
    def index() -> str:
        settings = current_app.config["settings"]
        return render_template(
            "index.html",
            working_copy=_get_working_copy(settings.converter_engine),
        )

    @app.get("/health")
    def health() -> tuple[dict[str, str], int]:
        return {"status": "ok"}, 200

    @app.post("/convert")
    def convert():
        upload = request.files.get("pdf_file")
        if upload is None or not upload.filename:
            return jsonify({"error": "Vui lòng chọn file PDF để chuyển đổi."}), 400

        original_name = Path(upload.filename).name
        if Path(original_name).suffix.lower() != ".pdf":
            return jsonify({"error": "Chỉ nhận file có đuôi .pdf."}), 400

        settings = current_app.config["settings"]
        converter = current_app.config["converter"]
        job_dir = Path(
            tempfile.mkdtemp(prefix="pdf-to-word-", dir=settings.temp_root)
        ).resolve()
        safe_stem = secure_filename(Path(original_name).stem) or "document"
        input_path = job_dir / f"{safe_stem}.pdf"
        output_path = job_dir / f"{safe_stem}.docx"

        try:
            upload.save(input_path)
            _ensure_pdf_signature(input_path)
            converter.convert(input_path, output_path)

            download_name = f"{Path(original_name).stem or 'converted'}.docx"
            response = send_file(
                output_path,
                as_attachment=True,
                download_name=download_name,
                mimetype=DOCX_MIMETYPE,
            )
            response.call_on_close(lambda: shutil.rmtree(job_dir, ignore_errors=True))
            return response
        except ConversionError as exc:
            current_app.logger.warning("Conversion failed: %s", exc)
            return _error_response(
                job_dir,
                message="Không thể chuyển PDF sang Word.",
                status_code=500,
                details=str(exc),
            )
        except ValueError as exc:
            return _error_response(job_dir, message=str(exc), status_code=400)
        except Exception:
            current_app.logger.exception("Unexpected server error during conversion.")
            return _error_response(
                job_dir,
                message="Có lỗi nội bộ khi xử lý file. Vui lòng thử lại.",
                status_code=500,
            )

    @app.errorhandler(RequestEntityTooLarge)
    def handle_file_too_large(_: RequestEntityTooLarge):
        settings = current_app.config["settings"]
        return (
            jsonify(
                {
                    "error": (
                        f"File vượt quá giới hạn {settings.upload_limit_mb} MB."
                    )
                }
            ),
            413,
        )

    return app


def _ensure_pdf_signature(file_path: Path) -> None:
    with file_path.open("rb") as uploaded_file:
        if uploaded_file.read(5) != b"%PDF-":
            raise ValueError("File tải lên không phải PDF hợp lệ.")


def _error_response(
    job_dir: Path, *, message: str, status_code: int, details: str | None = None
):
    shutil.rmtree(job_dir, ignore_errors=True)
    payload = {"error": message}
    if details:
        payload["details"] = details
    return jsonify(payload), status_code


def _get_working_copy(engine: str) -> str:
    normalized_engine = engine.strip().lower()
    if normalized_engine == "auto":
        return (
            "Server đang chuyển file, ưu tiên giữ header/footer và bố cục gần file gốc. "
            "Vui lòng chờ..."
        )

    if normalized_engine == "word":
        return "Server đang dùng Microsoft Word để chuyển file. Vui lòng chờ..."

    return "Server đang dùng pdf2docx để chuyển file. Vui lòng chờ..."
