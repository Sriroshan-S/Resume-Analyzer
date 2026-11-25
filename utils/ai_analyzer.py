import json
import os
import time
import traceback
from openai import OpenAI
from utils.ats_score import calculate_ats_score
from utils.resume_parser import extract_text_from_pdf

GROQ_BASE_URL = "https://api.groq.com/openai/v1"
GROQ_MODELS = [
    "openai/gpt-oss-20b",
    "openai/gpt-oss-120b",
    "llama-3.3-70b-versatile",
]

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

LIST_KEYS = {
    "suggestions",
    "interview_questions",
    "roadmap",
    "missing_skills",
    "strengths",
    "weaknesses",
    "career_recommendations",
}

STRING_KEYS = {"summary", "target_role"}

PROMPT_TEMPLATE = """
Analyze the resume text below. Respond with ONLY a valid JSON object (no markdown, no extra text)
using these exact keys:

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


def _is_retryable_error(exc):
    message = str(exc).upper()
    return (
        "503" in message
        or "UNAVAILABLE" in message
        or "429" in message
        or "RATE_LIMIT" in message
    )


def _ask_groq(text, api_key):
    """Send resume text to Groq's OpenAI-compatible Chat Completions API."""
    client = OpenAI(api_key=api_key, base_url=GROQ_BASE_URL)
    last_error = None

    for model_name in GROQ_MODELS:
        for attempt in range(3):
            try:
                response = client.chat.completions.create(
                    model=model_name,
                    messages=[
                        {
                            "role": "system",
                            "content": "You are a helpful resume analyzer that always outputs pure JSON.",
                        },
                        {
                            "role": "user",
                            "content": PROMPT_TEMPLATE.format(text=text[:12000]),
                        },
                    ],
                    response_format={"type": "json_object"},
                    temperature=0.3,
                )
                content = response.choices[0].message.content
                if not content:
                    raise ValueError("Empty response received from Groq.")
                return json.loads(_clean_json(content)), f"groq:{model_name}"
            except Exception as exc:
                last_error = exc
                if _is_retryable_error(exc) and attempt < 2:
                    wait_seconds = 2 * (attempt + 1)
                    print(
                        f"INFO: Groq {model_name} busy ({attempt + 1}/3); "
                        f"retrying in {wait_seconds}s..."
                    )
                    time.sleep(wait_seconds)
                    continue
                break

    raise last_error


def _apply_ai_result(result, ai_data):
    """Safely copy valid fields from Groq's response into result."""
    if not isinstance(ai_data, dict):
        return

    for key in LIST_KEYS:
        value = ai_data.get(key)
        if isinstance(value, list) and len(value) > 0:
            cleaned_items = [str(item).strip() for item in value if str(item).strip()]
            if cleaned_items:
                result[key] = cleaned_items

    for key in STRING_KEYS:
        value = ai_data.get(key)
        if isinstance(value, str) and value.strip():
            result[key] = value.strip()


def _build_skill_prompt(result):
    """Build a ready-to-copy prompt users can paste into an AI assistant to grow skills."""
    strengths = ", ".join(result.get("strengths", [])) or "Foundational programming skills"
    missing_skills = ", ".join(result.get("missing_skills", [])) or "Core technical skills"
    suggestions = " | ".join(result.get("suggestions", [])) or "Add measurable project impact"
    roadmap = " -> ".join(result.get("roadmap", [])) or "Build foundational projects"
    target_role = result.get("target_role", "Software Developer")
    summary = result.get("summary", "")
    score = result.get("score", 0)

    return (
        "Act as my personal tech mentor and career coach. Help me build a practical "
        "step-by-step plan to improve my skills and become job-ready based on my resume analysis:\n\n"
        f"- Target Role: {target_role}\n"
        f"- Current ATS Score: {score}/100\n"
        f"- Summary: {summary}\n"
        f"- Strengths: {strengths}\n"
        f"- Missing Skills to Learn: {missing_skills}\n"
        f"- Resume Improvements: {suggestions}\n"
        f"- Learning Roadmap: {roadmap}\n\n"
        "Please guide me through:\n"
        "1. A clear step-by-step study plan prioritizing my missing skills.\n"
        "2. 2-3 practical projects I can build to demonstrate these skills.\n"
        "3. Key concepts and practice exercises for each topic.\n"
        "4. Technical and behavioral interview questions based on my target role.\n"
        "5. How to write strong, metric-backed resume bullet points from my new projects.\n\n"
        "End with a quick question to help me pick my first task today."
    )


def analyze_resume(filepath):
    """Extract PDF text, compute ATS score, and generate AI insights via Groq."""
    result = {k: (list(v) if isinstance(v, list) else v) for k, v in DEFAULTS.items()}
    result["score"] = 0

    try:
        text = extract_text_from_pdf(filepath)
        result["score"] = calculate_ats_score(text)["score"]
    except Exception:
        print("PDF parsing or ATS scoring failed; returning defaults:")
        traceback.print_exc()
        result["skill_prompt"] = _build_skill_prompt(result)
        return result

    groq_key = os.getenv("GROQ_API_KEY")
    if not groq_key:
        print("INFO: GROQ_API_KEY not set. Using default suggestions.")
        result["skill_prompt"] = _build_skill_prompt(result)
        return result

    try:
        ai_data, used_model = _ask_groq(text, groq_key)
        _apply_ai_result(result, ai_data)
        print(f"INFO: Live Groq analysis succeeded using {used_model}.")
    except Exception:
        print("WARNING: Groq call failed; using default suggestions:")
        traceback.print_exc()

    result["skill_prompt"] = _build_skill_prompt(result)
    return result