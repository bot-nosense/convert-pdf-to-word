from __future__ import annotations

import io
from pathlib import Path

import pytest

from pdf_word_server.app import DOCX_MIMETYPE, create_app
from pdf_word_server.config import Settings


class StubConverter:
    def convert(self, input_path: Path, output_path: Path) -> None:
        assert input_path.exists()
        output_path.write_bytes(b"fake-docx-content")


@pytest.fixture()
def client(tmp_path: Path):
    settings = Settings(
        host="127.0.0.1",
        port=8080,
        converter_engine="pdf2docx",
        upload_limit_mb=5,
        word_timeout_seconds=30,
        temp_root=tmp_path / "work",
    )
    app = create_app(settings)
    app.config["TESTING"] = True
    app.config["converter"] = StubConverter()
    return app.test_client()


def test_healthcheck(client) -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.get_json() == {"status": "ok"}


def test_rejects_missing_upload(client) -> None:
    response = client.post("/convert", data={}, content_type="multipart/form-data")

    assert response.status_code == 400
    assert response.get_json()["error"] == "Vui lòng chọn file PDF để chuyển đổi."


def test_rejects_non_pdf_upload(client) -> None:
    response = client.post(
        "/convert",
        data={"pdf_file": (io.BytesIO(b"hello"), "note.txt")},
        content_type="multipart/form-data",
    )

    assert response.status_code == 400
    assert response.get_json()["error"] == "Chỉ nhận file có đuôi .pdf."


def test_converts_pdf_and_returns_docx(client) -> None:
    fake_pdf = b"%PDF-1.4\n1 0 obj\n<<>>\nendobj\ntrailer\n<<>>\n%%EOF"
    response = client.post(
        "/convert",
        data={"pdf_file": (io.BytesIO(fake_pdf), "proposal.pdf")},
        content_type="multipart/form-data",
    )

    assert response.status_code == 200
    assert response.mimetype == DOCX_MIMETYPE
    assert response.headers["Content-Disposition"]
    assert "proposal.docx" in response.headers["Content-Disposition"]
    assert response.data == b"fake-docx-content"
