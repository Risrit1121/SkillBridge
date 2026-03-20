import json
from pathlib import Path
from fastapi import APIRouter
from backend.models.job import JobDescription

router = APIRouter(prefix="/jobs", tags=["jobs"])
JD_PATH = Path(__file__).parent.parent.parent / "data" / "job_descriptions.json"

def load_jobs() -> list[dict]:
    if JD_PATH.exists():
        with open(JD_PATH) as f:
            return json.load(f)
    return []

@router.get("", response_model=list[JobDescription])
def get_jobs(category: str = "", search: str = ""):
    jobs = load_jobs()
    if category:
        jobs = [j for j in jobs if j.get("category", "").lower() == category.lower()]
    if search:
        s = search.lower()
        jobs = [j for j in jobs if s in j["title"].lower() or s in j["description"].lower()]
    return jobs
