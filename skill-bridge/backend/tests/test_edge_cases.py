import pytest
from httpx import AsyncClient, ASGITransport
from unittest.mock import patch
from backend.main import app

@pytest.mark.asyncio
async def test_analyze_empty_resume():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.post("/analyze", json={
            "resume_text": "   ",
            "job_description": "Some JD",
            "required_skills": ["Python"],
        })
    assert resp.status_code == 400

@pytest.mark.asyncio
async def test_analyze_no_matching_skills():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.post("/analyze", json={
            "resume_text": "I enjoy hiking and cooking.",
            "job_description": "Need a Kubernetes expert.",
            "required_skills": ["Kubernetes", "Docker", "Terraform"],
        })
    assert resp.status_code == 200
    data = resp.json()
    assert data["match_score"] == 0.0
    assert len(data["missing_skills"]) == 3

@pytest.mark.asyncio
async def test_analyze_ai_down_uses_fallback():
    with patch("backend.services.gap_analyzer.call_ai", side_effect=Exception("API down")):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            resp = await client.post("/analyze", json={
                "resume_text": "Python developer with Docker experience.",
                "job_description": "Need Python and Kubernetes.",
                "required_skills": ["Python", "Kubernetes"],
            })
    assert resp.status_code == 200
    data = resp.json()
    assert "match_score" in data

@pytest.mark.asyncio
async def test_roadmap_empty_skills():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.get("/roadmap?target_role=Engineer&missing_skills=")
    assert resp.status_code == 200
    data = resp.json()
    assert data["steps"] == []
    assert data["total_weeks"] == 0

@pytest.mark.asyncio
async def test_jobs_search():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.get("/jobs?search=python")
    assert resp.status_code == 200
    results = resp.json()
    assert all("python" in j["title"].lower() or "python" in j["description"].lower() for j in results)
