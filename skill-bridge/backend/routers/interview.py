from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from backend.services.interview_generator import generate_questions, chat_interview

router = APIRouter(prefix="/interview", tags=["interview"])

class InterviewRequest(BaseModel):
    skills: list[str]
    target_role: str = "Software Engineer"
    num_questions: int = 8

class ChatMessage(BaseModel):
    role: str   # "user" | "assistant"
    content: str

class ChatRequest(BaseModel):
    messages: list[ChatMessage]
    skills: list[str]
    target_role: str = "Software Engineer"

@router.post("")
async def interview(req: InterviewRequest):
    if not req.skills:
        raise HTTPException(400, "skills list is required")
    return await generate_questions(req.skills, req.target_role, req.num_questions)

@router.post("/chat")
async def interview_chat(req: ChatRequest):
    if not req.messages:
        raise HTTPException(400, "messages required")
    reply = await chat_interview(req.messages, req.skills, req.target_role)
    return {"reply": reply}
