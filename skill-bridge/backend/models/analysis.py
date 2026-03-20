from pydantic import BaseModel

class SkillGap(BaseModel):
    missing_skills: list[str]
    matched_skills: list[str]
    match_score: float
    summary: str
    certifications: list[str] = []
    resume_positives: list[str] = []
    resume_improvements: list[str] = []

class RoadmapStep(BaseModel):
    order: int
    skill: str
    resource: str
    duration_weeks: int

class Roadmap(BaseModel):
    target_role: str
    steps: list[RoadmapStep]
    total_weeks: int
