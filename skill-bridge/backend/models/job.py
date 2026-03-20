from pydantic import BaseModel
from typing import Optional

class JobDescription(BaseModel):
    id: str
    title: str
    company: str
    description: str
    required_skills: list[str]
    category: Optional[str] = None
