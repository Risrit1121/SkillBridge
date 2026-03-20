from fastapi import APIRouter
from backend.services.roadmap_builder import build_roadmap
from backend.models.analysis import Roadmap

router = APIRouter(prefix="/roadmap", tags=["roadmap"])

@router.get("", response_model=Roadmap)
async def roadmap(target_role: str = "Software Engineer", missing_skills: str = ""):
    skills = [s.strip() for s in missing_skills.split(",") if s.strip()]
    return await build_roadmap(target_role, skills)
