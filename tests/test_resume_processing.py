import pytest

from utils.resume_parser import extract_text_from_pdf, clean_text
from utils.ats_score import extract_skills, calculate_ats_score
from utils.career import recommend_careers


def test_non_pdf_file_is_rejected():
    with pytest.raises(ValueError):
        extract_text_from_pdf("resume.txt")


def test_missing_pdf_raises_error():
    with pytest.raises(FileNotFoundError):
        extract_text_from_pdf("does_not_exist.pdf")


def test_clean_text_removes_blank_lines():
    assert clean_text("Hello\n\n  World  ") == "Hello\nWorld"


def test_extract_skills_finds_python_and_sql():
    skills = extract_skills("I know Python and SQL.")
    assert "python" in skills
    assert "sql" in skills


def test_java_is_not_matched_inside_javascript():
    assert "java" not in extract_skills("I know JavaScript.")


def test_empty_resume_raises_error():
    with pytest.raises(ValueError):
        calculate_ats_score("")


def test_score_is_between_0_and_100():
    result = calculate_ats_score("Education: B.Tech. Skills: Python. Project: web app. email a@b.com")
    assert 0 <= result["score"] <= 100


def test_careers_are_sorted_best_first():
    careers = recommend_careers(["python", "sql", "excel", "statistics", "data analysis", "power bi"])
    assert careers[0]["career"] == "Data Analyst"
    assert careers[0]["match_percent"] == 100


def test_careers_reject_non_list():
    with pytest.raises(ValueError):
        recommend_careers("python")