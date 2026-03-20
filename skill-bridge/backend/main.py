from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.routers import analyze, roadmap, jobs, interview

app = FastAPI(title="SkillBridge API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(analyze.router)
app.include_router(roadmap.router)
app.include_router(jobs.router)
app.include_router(interview.router)

@app.get("/health")
def health():
    return {"status": "ok"}
