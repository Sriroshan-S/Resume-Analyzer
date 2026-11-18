import pytest
from utils.ai_analyzer import analyze_resume


def test_analyze_resume_returns_dict():
    result = analyze_resume("dummy_resume.pdf")
    assert isinstance(result, dict)
    assert "score" in result
    assert "suggestions" in result
    assert isinstance(result["suggestions"], list)
    assert 0 <= result["score"] <= 100