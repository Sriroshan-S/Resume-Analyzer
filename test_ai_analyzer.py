from utils.ai_analyzer import analyze_resume


def test_analyze_resume_fallback():
    result = analyze_resume("non_existent_file.pdf")

    assert "score" in result
    assert "suggestions" in result
    assert "summary" in result
    assert "interview_questions" in result
    assert "missing_skills" in result
    assert "strengths" in result
    assert "weaknesses" in result
    assert "career_recommendations" in result
    assert "target_role" in result
    assert "roadmap" in result

    assert isinstance(result["score"], (int, float))
    assert isinstance(result["suggestions"], list)
    assert isinstance(result["missing_skills"], list)