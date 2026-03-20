from backend.fallback.skill_matcher import extract_skills

def parse_resume(text: str) -> dict:
    """Return raw text + extracted skills list."""
    skills = extract_skills(text)
    return {"raw_text": text, "skills": skills}
