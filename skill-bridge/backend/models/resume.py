from pydantic import BaseModel
from typing import Optional

class ResumeTextInput(BaseModel):
    text: str
    target_role: Optional[str] = None

class ResumeSkills(BaseModel):
    raw_text: str
    skills: list[str]
