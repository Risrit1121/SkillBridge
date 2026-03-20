from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from backend.services.resume_parser import parse_resume
from backend.services.gap_analyzer import analyze_gap
from backend.models.analysis import SkillGap

router = APIRouter(prefix="/analyze", tags=["analyze"])

class AnalyzeRequest(BaseModel):
    resume_text: str
    job_description: str
    required_skills: list[str] = []
    target_role: str = "Software Engineer"

@router.post("", response_model=SkillGap)
async def analyze(req: AnalyzeRequest):
    if not req.resume_text.strip():
        raise HTTPException(400, "resume_text is required")
    parsed = parse_resume(req.resume_text)
    result = await analyze_gap(
        parsed["skills"], req.required_skills, req.job_description,
        resume_text=req.resume_text, target_role=req.target_role,
    )
    return result
