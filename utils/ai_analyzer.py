import os
import json
import traceback
import google.generativeai as genai
from utils.resume_parser import extract_text_from_pdf
from utils.ats_score import calculate_ats_score

# Configure Gemini using an environment variable
API_KEY = os.getenv("GEMINI_API_KEY")
if API_KEY:
    genai.configure(api_key=API_KEY)

# gemini-pro is retired. Run genai.list_models() to confirm what your key supports.
MODEL_NAME = "gemini-2.5-flash"

# Used only when Gemini is unavailable or returns something unusable.
# Keys match what app.py reads: suggestions, summary, roadmap, interview_questions
DEFAULTS = {
    "suggestions": [
        "Add a strong professional summary at the top.",
        "Include quantifiable metrics in your projects.",
        "Ensure your GitHub and LinkedIn links are clickable.",
        "Highlight key technologies used in your projects.",
    ],
    "summary": "Motivated IT student eager to build scalable software solutions.",
    "interview_questions": [
        "Explain a project from your resume.",
        "What is Flask and how does routing work?",
        "How do you handle exceptions in Python?",
    ],
    "roadmap": [
        "Learn Advanced Python",
        "Master Flask",
        "Build Full-Stack Projects",
        "Learn Git Workflows",
        "Deploy to Cloud",
    ],
    "missing_skills": ["SQL", "Docker", "Git Advanced", "CI/CD", "REST APIs"],
    "strengths": ["Strong Python basics", "Good project structure"],
    "weaknesses": ["Needs more metrics", "Add certifications"],
    "career_recommendations": ["Software Engineer", "Web Developer"],
    "target_role": "Full Stack Developer",
}

PROMPT_TEMPLATE = """
Analyze the resume text below. Respond with ONLY a JSON object, no markdown,
using exactly these keys:

{{
  "suggestions": ["4 actionable resume improvements"],
  "summary": "A professional 2-line summary",
  "interview_questions": ["4-5 technical/HR interview questions"],
  "missing_skills": ["5 missing technical skills for growth"],
  "strengths": ["2 strong points"],
  "weaknesses": ["2 weak areas"],
  "career_recommendations": ["4 suitable job roles"],
  "target_role": "One target role",
  "roadmap": ["5 learning steps toward the target role"]
}}

Resume Text:
{text}
"""


def _clean_json(raw):
    """Remove markdown code fences if the model added them."""
    raw = raw.strip()
    if raw.startswith("```"):
        raw = raw.strip("`").strip()
        if raw.lower().startswith("json"):
            raw = raw[4:].strip()
    return raw


def _ask_gemini(text):
    model = genai.GenerativeModel(MODEL_NAME)
    response = model.generate_content(
        PROMPT_TEMPLATE.format(text=text[:12000]),
        generation_config={"response_mime_type": "application/json"},
    )
    return json.loads(_clean_json(response.text))


def analyze_resume(filepath):
    """Extracts text, calculates ATS score, and generates AI insights."""
    result = dict(DEFAULTS)
    result["score"] = 0

    # 1. Parse the PDF and compute the ATS score
    try:
        text = extract_text_from_pdf(filepath)
        result["score"] = calculate_ats_score(text)["score"]
    except Exception:
        traceback.print_exc()
        return result

    # 2. Ask Gemini and overwrite defaults with whatever it returns
    if not API_KEY:
        print("WARNING: GEMINI_API_KEY is not set. Returning default suggestions.")
        return result

    try:
        ai = _ask_gemini(text)
        for key in DEFAULTS:
            if ai.get(key):
                result[key] = ai[key]
        print("Gemini analysis succeeded.")
    except Exception:
        print("Gemini call failed, using defaults:")
        traceback.print_exc()

    return result
