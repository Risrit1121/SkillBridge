import json
from backend.services.ai_client import call_ai

RESOURCES = {
    "Python": "https://docs.python.org/3/tutorial/",
    "React": "https://react.dev/learn",
    "Docker": "https://docs.docker.com/get-started/",
    "AWS": "https://aws.amazon.com/training/",
    "Kubernetes": "https://kubernetes.io/docs/tutorials/",
    "Machine Learning": "https://www.coursera.org/learn/machine-learning",
    "SQL": "https://sqlzoo.net/",
    "TypeScript": "https://www.typescriptlang.org/docs/",
}
DEFAULT_RESOURCE = "https://www.google.com/search?q=learn+"

PROMPT_TEMPLATE = """
You are a learning path designer. Given missing skills for a target role, return a JSON array of steps:
[{{"order":1,"skill":"...","resource":"<url>","duration_weeks":<int>}}, ...]

Target role: {role}
Missing skills: {missing}

Respond ONLY with a valid JSON array.
"""

async def build_roadmap(target_role: str, missing_skills: list[str]) -> dict:
    steps = []
    try:
        prompt = PROMPT_TEMPLATE.format(role=target_role, missing=missing_skills)
        raw = await call_ai(prompt)
        raw = raw.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
        ai_steps = json.loads(raw)
        steps = [
            {"order": s.get("order", i+1), "skill": s["skill"],
             "resource": s.get("resource", DEFAULT_RESOURCE + s["skill"].replace(" ", "+")),
             "duration_weeks": s.get("duration_weeks", 2)}
            for i, s in enumerate(ai_steps)
        ]
    except Exception:
        for i, skill in enumerate(missing_skills):
            steps.append({
                "order": i + 1,
                "skill": skill,
                "resource": RESOURCES.get(skill, DEFAULT_RESOURCE + skill.replace(" ", "+")),
                "duration_weeks": 2,
            })

    total = sum(s["duration_weeks"] for s in steps)
    return {"target_role": target_role, "steps": steps, "total_weeks": total}
