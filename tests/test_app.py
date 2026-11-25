import io

import pytest

from app import app
from utils.analyzer import analyze_resume


def _make_sample_pdf_bytes(text: str = "Sample Resume Python Flask") -> bytes:
    stream = f"BT /F1 12 Tf 72 720 Td ({text}) Tj ET".encode("latin-1")
    objects = [
        b"1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n",
        b"2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n",
        (
            b"3 0 obj\n<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] "
            b"/Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >>\nendobj\n"
        ),
        b"4 0 obj\n<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>\nendobj\n",
        f"5 0 obj\n<< /Length {len(stream)} >>\nstream\n".encode("latin-1")
        + stream
        + b"\nendstream\nendobj\n",
    ]

    pdf = bytearray(b"%PDF-1.4\n")
    offsets = [0]
    for obj in objects:
        offsets.append(len(pdf))
        pdf.extend(obj)

    xref_pos = len(pdf)
    pdf.extend(f"xref\n0 {len(offsets)}\n".encode("latin-1"))
    pdf.extend(b"0000000000 65535 f \n")
    for off in offsets[1:]:
        pdf.extend(f"{off:010d} 00000 n \n".encode("latin-1"))

    pdf.extend(
        f"trailer\n<< /Size {len(offsets)} /Root 1 0 R >>\nstartxref\n{xref_pos}\n%%EOF\n".encode(
            "latin-1"
        )
    )
    return bytes(pdf)


@pytest.fixture
def client(tmp_path):
    app.config["TESTING"] = True
    app.config["UPLOAD_FOLDER"] = str(tmp_path)
    with app.test_client() as client:
        yield client


def test_home_page_loads(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b"Resume Analyzer" in response.data


def test_analyze_without_file(client):
    response = client.post("/analyze", data={}, content_type="multipart/form-data")
    assert response.status_code == 400


def test_analyze_rejects_non_pdf(client):
    data = {"resume": (io.BytesIO(b"hello"), "notes.txt")}
    response = client.post("/analyze", data=data, content_type="multipart/form-data")
    assert response.status_code == 400


def test_analyze_accepts_pdf(client):
    data = {"resume": (io.BytesIO(b"%PDF-1.4 fake content"), "resume.pdf")}
    response = client.post("/analyze", data=data, content_type="multipart/form-data")
    assert response.status_code == 200
    assert b"Analysis Result" in response.data


def test_analyzer_returns_valid_result(tmp_path):
    sample_pdf = tmp_path / "sample_resume.pdf"
    sample_pdf.write_bytes(_make_sample_pdf_bytes())

    result = analyze_resume(str(sample_pdf))
    assert 0 <= result["score"] <= 100
    assert isinstance(result["suggestions"], list)

