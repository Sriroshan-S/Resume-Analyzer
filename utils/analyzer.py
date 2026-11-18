from utils.resume_parser import extract_text_from_pdf
from utils.ats_score import calculate_ats_score
from utils.career import recommend_careers

MAX_POINTS = {
    "skills": 25,
    "education": 15,
    "projects": 15,
    "experience": 15,
    "certifications": 10,
    "length": 10,
    "contact": 10,
}

TIPS = {
    "skills": "Add more relevant technical skills to your skills section.",
    "education": "Add a clear Education section with your degree and college.",
    "projects": "List your projects with the technologies you used.",
    "experience": "Add internships, training or any practical experience.",
    "certifications": "Add certifications or online courses you have completed.",
    "length": "Keep your resume between about 150 and 800 words.",
    "contact": "Add both a professional email and a phone number.",
}


def build_suggestions(breakdown):
    """Make one suggestion for every area where points were lost."""
    suggestions = []
    for area, max_points in MAX_POINTS.items():
        if breakdown.get(area, 0) < max_points:
            suggestions.append(TIPS[area])
    return suggestions


def analyze_resume(filepath):
    """Analyze a resume PDF and return score, suggestions and career matches."""
    text = extract_text_from_pdf(filepath)
    result = calculate_ats_score(text)
    careers = recommend_careers(result["skills_found"])

    return {
        "score": result["score"],
        "suggestions": build_suggestions(result["breakdown"]),
        "breakdown": result["breakdown"],
        "skills_found": result["skills_found"],
        "careers": careers[:3],
    }