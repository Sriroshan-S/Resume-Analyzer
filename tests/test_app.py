import io

import pytest

from app import app
from utils.analyzer import analyze_resume


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


def test_analyzer_returns_valid_result():
    import os
    pdf_path = os.path.join(os.path.dirname(__file__), "sample_resume.pdf")
    result = analyze_resume(pdf_path)
    assert 0 <= result["score"] <= 100
    assert isinstance(result["suggestions"], list)