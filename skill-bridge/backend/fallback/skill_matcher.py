import json
import re
from pathlib import Path

TAXONOMY_PATH = Path(__file__).parent / "skill_taxonomy.json"

def load_taxonomy() -> dict[str, list[str]]:
    with open(TAXONOMY_PATH) as f:
        return json.load(f)

def extract_skills(text: str) -> list[str]:
    taxonomy = load_taxonomy()
    text_lower = text.lower()
    found = set()
    for skills in taxonomy.values():
        for skill in skills:
            pattern = r'\b' + re.escape(skill.lower()) + r'\b'
            if re.search(pattern, text_lower):
                found.add(skill)
    return sorted(found)

def compute_gap(resume_skills: list[str], jd_skills: list[str]) -> dict:
    resume_set = {s.lower() for s in resume_skills}
    jd_set = {s.lower() for s in jd_skills}
    matched = [s for s in jd_skills if s.lower() in resume_set]
    missing = [s for s in jd_skills if s.lower() not in resume_set]
    score = len(matched) / len(jd_set) if jd_set else 0.0
    return {"matched": matched, "missing": missing, "score": round(score, 2)}
