import re

SKILLS_LIST = [
    "python", "java", "c++", "javascript", "html", "css", "flask",
    "django", "react", "sql", "excel", "power bi", "git", "github",
    "machine learning", "data analysis", "statistics", "numpy", "pandas",
]


def extract_skills(text):
    """Return the skills from SKILLS_LIST that appear in the text."""
    text_lower = text.lower()
    found = []
    for skill in SKILLS_LIST:
        pattern = r"(?<![a-z0-9])" + re.escape(skill) + r"(?![a-z0-9])"
        if re.search(pattern, text_lower):
            found.append(skill)
    return found


def has_any(text, words):
    """Return True if any of the words appear in the text."""
    text_lower = text.lower()
    for word in words:
        if word in text_lower:
            return True
    return False


def calculate_ats_score(text):
    """Score a resume out of 100 and show how the points were earned."""
    if not text or text.strip() == "":
        raise ValueError("Resume text is empty.")

    skills_found = extract_skills(text)
    breakdown = {}

    breakdown["skills"] = min(len(skills_found) * 2.5, 25)
    breakdown["education"] = 15 if has_any(text, ["education", "b.tech", "bachelor", "degree", "university", "college"]) else 0
    breakdown["projects"] = 15 if has_any(text, ["project"]) else 0
    breakdown["experience"] = 15 if has_any(text, ["experience", "internship"]) else 0
    breakdown["certifications"] = 10 if has_any(text, ["certification", "certificate", "course"]) else 0

    word_count = len(text.split())
    if 150 <= word_count <= 800:
        breakdown["length"] = 10
    elif 50 <= word_count < 150 or word_count > 800:
        breakdown["length"] = 5
    else:
        breakdown["length"] = 0

    has_email = re.search(r"[\w.+-]+@[\w-]+\.[\w.]+", text) is not None
    has_phone = re.search(r"\+?\d[\d\s\-]{8,}\d", text) is not None
    breakdown["contact"] = (5 if has_email else 0) + (5 if has_phone else 0)

    total = round(sum(breakdown.values()))
    return {"score": total, "breakdown": breakdown, "skills_found": skills_found}


if __name__ == "__main__":
    from resume_parser import extract_text_from_pdf

    resume_text = extract_text_from_pdf("sample_resume.pdf")
    result = calculate_ats_score(resume_text)
    print("ATS Score:", result["score"], "/ 100")
    print("Skills found:", result["skills_found"])
    print("Breakdown:", result["breakdown"])