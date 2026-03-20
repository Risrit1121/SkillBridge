import pytest
from httpx import AsyncClient, ASGITransport
from backend.main import app

@pytest.mark.asyncio
async def test_analyze_happy_path():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.post("/analyze", json={
            "resume_text": "Experienced Python developer with FastAPI, Docker, and PostgreSQL skills.",
            "job_description": "We need a Python backend engineer with FastAPI and Docker.",
            "required_skills": ["Python", "FastAPI", "Docker", "AWS"],
            "target_role": "Backend Engineer",
        })
    assert resp.status_code == 200
    data = resp.json()
    assert "missing_skills" in data
    assert "matched_skills" in data
    assert 0.0 <= data["match_score"] <= 1.0
    assert isinstance(data["summary"], str)

@pytest.mark.asyncio
async def test_jobs_returns_list():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.get("/jobs")
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)
    assert len(resp.json()) > 0

@pytest.mark.asyncio
async def test_jobs_filter_by_category():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.get("/jobs?category=backend")
    assert resp.status_code == 200
    for job in resp.json():
        assert job["category"] == "backend"

@pytest.mark.asyncio
async def test_roadmap_returns_steps():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.get("/roadmap?target_role=ML+Engineer&missing_skills=PyTorch,Docker")
    assert resp.status_code == 200
    data = resp.json()
    assert data["target_role"] == "ML Engineer"
    assert len(data["steps"]) == 2
    assert data["total_weeks"] > 0
