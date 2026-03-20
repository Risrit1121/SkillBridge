import json
from backend.config import settings

SYSTEM_PROMPT = """You are a professional senior technical interviewer conducting a mock interview for a {role} position.
The candidate's resume shows these skills: {skills}.

Strict rules:
- FIRST message only: greet warmly, introduce yourself, wish them luck, then ask your first question.
- Every question MUST be directly based on the candidate's listed skills OR the {role} role requirements.
- Never ask generic questions unrelated to their skills or role.
- After each answer: give 1-2 sentence feedback, then ask the next skill/role-specific question.
- Increase difficulty gradually: easy → medium → hard.
- After 6-8 exchanges: give a warm closing summary and score out of 10.
- Be concise. Stay in character."""

FALLBACK_REPLIES = [
    "Welcome! I'm your interviewer for this {role} session. Great to have you here — best of luck! Let's start: Can you walk me through how you've used {skill} in a real project?",
    "Good answer! Now, as a {role}, how would you handle a production issue related to {skill2}?",
    "Interesting. Can you explain the core design principles you follow when building systems with {skill}?",
    "Nice. How would you approach scaling a {role} system under heavy traffic?",
    "Good thinking. What's the most challenging problem you've solved using {skill}, and how did you approach it?",
    "Well done! You've shown solid knowledge throughout. As a final score, I'd rate this interview **7/10**. Strong fundamentals in {skill} — work on system design depth to reach the next level. 🎉",
]

async def chat_interview(messages: list, skills: list[str], target_role: str) -> str:
    """Multi-turn interview chat via Ollama Cloud, falls back to OpenRouter, then canned replies."""
    from backend.config import settings

    key = settings.ollama_key or settings.active_openrouter_key
    if not key:
        raise ValueError("No key")

    from openai import AsyncOpenAI

    if settings.ollama_key:
        client = AsyncOpenAI(api_key=settings.ollama_key, base_url="https://ollama.com/v1")
        model = "gemma3:12b"
    else:
        client = AsyncOpenAI(api_key=settings.active_openrouter_key, base_url="https://openrouter.ai/api/v1")
        model = "openai/gpt-4o-mini"

    system = SYSTEM_PROMPT.format(role=target_role, skills=", ".join(skills))
    chat_messages = [{"role": "system", "content": system}]
    for m in messages:
        # handle both Pydantic objects and plain dicts
        role = m.role if hasattr(m, "role") else m["role"]
        content = m.content if hasattr(m, "content") else m["content"]
        chat_messages.append({"role": role, "content": content})

    try:
        resp = await client.chat.completions.create(model=model, messages=chat_messages)
        return resp.choices[0].message.content
    except Exception:
        idx = min(len(messages) - 1, len(FALLBACK_REPLIES) - 1)
        reply = FALLBACK_REPLIES[idx]
        skill = skills[0] if skills else "your primary skill"
        role_skill = skills[1] if len(skills) > 1 else skill
        return reply.replace("{role}", target_role).replace("{skill}", skill).replace("{skill2}", role_skill)


# ── original batch question generator (kept for non-chat flow) ────────────────

PROMPT = """
You are a senior technical interviewer. Generate {n} interview questions for a {role} candidate.
Focus specifically on these skills: {skills}.
Mix: conceptual, practical, scenario-based questions.
Return JSON array: [{{"question":"...","skill":"...","type":"conceptual|practical|scenario","difficulty":"easy|medium|hard"}}]
Respond ONLY with valid JSON.
"""

FALLBACK_QUESTIONS = {
    "Python": [("What are Python decorators and when would you use them?", "conceptual", "medium"),
               ("How does Python's GIL affect multi-threaded programs?", "conceptual", "hard")],
    "Docker": [("Explain the difference between a Docker image and a container.", "conceptual", "easy"),
               ("How would you reduce the size of a Docker image?", "practical", "medium")],
    "AWS":    [("What is the difference between S3 and EBS?", "conceptual", "easy"),
               ("How would you design a highly available web app on AWS?", "scenario", "hard")],
    "React":  [("Explain the difference between state and props.", "conceptual", "easy"),
               ("How does React's virtual DOM work?", "conceptual", "medium")],
    "Kubernetes": [("What is the role of a Kubernetes pod vs a deployment?", "conceptual", "medium"),
                   ("How would you handle a failing pod in production?", "scenario", "hard")],
}

async def generate_questions(skills: list[str], target_role: str, n: int) -> dict:
    from backend.services.ai_client import call_ai
    try:
        prompt = PROMPT.format(n=n, role=target_role, skills=", ".join(skills))
        raw = await call_ai(prompt)
        raw = raw.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
        questions = json.loads(raw)
        return {"target_role": target_role, "skills": skills, "questions": questions}
    except Exception:
        questions = []
        for skill in skills:
            for q, qtype, diff in FALLBACK_QUESTIONS.get(skill, []):
                questions.append({"question": q, "skill": skill, "type": qtype, "difficulty": diff})
                if len(questions) >= n:
                    break
        if not questions:
            questions = [{"question": f"Describe your experience with {s}.", "skill": s,
                          "type": "conceptual", "difficulty": "easy"} for s in skills[:n]]
        return {"target_role": target_role, "skills": skills, "questions": questions}
