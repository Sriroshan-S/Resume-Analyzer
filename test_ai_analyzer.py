from utils.ai_analyzer import analyze_resume
import os

def test_analyze_resume_fallback():
    # Test with a dummy file path to trigger the safe fallback structure
    result = analyze_resume("non_existent_file.pdf")
    
    # Assertions to ensure all required dashboard keys are present
    assert "score" in result
    assert "ai_suggestions" in result
    assert "professional_summary" in result
    assert "interview_questions" in result
    assert "missing_skills" in result
    assert "resume_strength" in result
    assert "career_recommendations" in result
    assert "career_roadmap" in result
    
    # Check data types
    assert isinstance(result["score"], (int, float))
    assert isinstance(result["ai_suggestions"], list)
    assert isinstance(result["missing_skills"], list)