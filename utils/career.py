CAREER_SKILLS = {
    "Software Engineer": ["python", "java", "c++", "git", "github", "sql"],
    "Web Developer": ["html", "css", "javascript", "react", "flask", "git"],
    "AI Engineer": ["python", "machine learning", "numpy", "pandas", "statistics"],
    "Data Analyst": ["python", "sql", "excel", "power bi", "statistics", "data analysis"],
    "Backend Developer": ["python", "flask", "django", "sql", "git", "github"],
}


def recommend_careers(skills_found):
    """Rank careers by how many of their required skills the resume has."""
    if not isinstance(skills_found, list):
        raise ValueError("skills_found must be a list.")

    results = []
    for career, required in CAREER_SKILLS.items():
        matched = [skill for skill in required if skill in skills_found]
        missing = [skill for skill in required if skill not in skills_found]
        percent = round(len(matched) / len(required) * 100)
        results.append({
            "career": career,
            "match_percent": percent,
            "matched_skills": matched,
            "missing_skills": missing,
        })

    results.sort(key=lambda item: item["match_percent"], reverse=True)
    return results


if __name__ == "__main__":
    from resume_parser import extract_text_from_pdf
    from ats_score import extract_skills

    text = extract_text_from_pdf("sample_resume.pdf")
    skills = extract_skills(text)
    print("Skills found:", skills)
    for item in recommend_careers(skills):
        print(item["career"], "-", item["match_percent"], "%")
        print("   Missing:", item["missing_skills"])