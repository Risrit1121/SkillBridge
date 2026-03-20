# 🌉 SkillBridge — AI-Powered Skill Gap Analyzer

SkillBridge analyzes a candidate's resume against a job description, identifies skill gaps, and generates a personalized learning roadmap.

---

## Problem Statement

Job seekers struggle to understand exactly which skills they're missing for a target role. SkillBridge bridges that gap with AI-powered analysis and actionable learning paths.

---

## ✅ Minimum Requirements Compliance

### 1. Core End-to-End Flow (Create + View + Update + Search)

| Step | Endpoint/UI | Action |
|------|-------------|--------|
| **CREATE** | `POST /analyze` + Frontend Upload | User uploads/pastes resume text. System extracts skills and creates an analysis. |
| **VIEW** | `GET /jobs` + Frontend Dashboard | User views job descriptions, match scores, skill gaps, and resume feedback. |
| **UPDATE** | `GET /roadmap` + Frontend Roadmap | User generates personalized learning roadmap based on missing skills. |
| **SEARCH/FILTER** | `GET /jobs?category=X&search=Y` | Browse JDs by category (backend, frontend, etc.) or keyword search. |

**Full User Journey:**
1. Upload resume → AI extracts skills
2. Select target role → System compares against 20+ JDs
3. View gap analysis → See match score, missing skills, certifications, resume tips
4. Generate roadmap → Get step-by-step learning plan with resources
5. Browse jobs → Filter by category/keywords to explore opportunities

---

### 2. AI Integration + Fallback

**AI Capability: SKILL EXTRACTION & GAP ANALYSIS**

| Component | AI Function | Fallback When AI Unavailable |
|-----------|-------------|------------------------------|
| `gap_analyzer.py` | Uses LLM to analyze resume vs job, generate summary, certifications, resume feedback | `skill_matcher.py` — rule-based regex matching against `skill_taxonomy.json` |
| `roadmap_builder.py` | Uses LLM to generate personalized learning steps with timelines | Static resource mapping (`RESOURCES` dict) with default Google search links |
| `interview_generator.py` | Uses LLM for interactive interview chat | `FALLBACK_REPLIES` — canned questions based on role/skill templates |

**Fallback Behavior:**
- All AI calls wrapped in try/except
- If API fails or no key configured → immediately switches to rule-based fallback
- User experience is seamless — no errors, just slightly less personalized results
- **Test coverage:** `test_analyze_ai_down_uses_fallback` explicitly validates this

---

---

## Architecture

```
frontend/app.py          ← Streamlit UI
      │
      ▼ HTTP
backend/main.py          ← FastAPI app
  ├── POST /analyze      ← Gap analysis
  ├── GET  /roadmap      ← Learning roadmap
  └── GET  /jobs         ← Browse JDs
      │
      ├── services/
      │   ├── resume_parser.py    ← Skill extraction
      │   ├── gap_analyzer.py     ← AI + fallback gap analysis
      │   ├── roadmap_builder.py  ← AI + fallback roadmap
      │   └── ai_client.py        ← OpenAI / Anthropic wrapper
      │
      └── fallback/
          ├── skill_matcher.py    ← Rule-based keyword matching
          └── skill_taxonomy.json ← Master skill list
```

---

## Setup

### 1. Clone & install

```bash
git clone <repo-url>
cd skill-bridge
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
```

### 2. Configure environment

```bash
cp .env.example .env
# Edit .env and add your API key(s)
```

| Variable | Description |
|---|---|
| `OPENAI_API_KEY` | OpenAI API key |
| `ANTHROPIC_API_KEY` | Anthropic (Claude) API key |
| `AI_PROVIDER` | `openai` \| `anthropic` \| `fallback` |
| `MODEL_NAME` | e.g. `gpt-4o-mini`, `claude-3-haiku-20240307` |

> If no API key is set, the app automatically uses rule-based fallback logic — no AI required.

### 3. Run the backend

```bash
uvicorn backend.main:app --reload
# API available at http://localhost:8000
# Docs at http://localhost:8000/docs
```

### 4. Run the frontend

```bash
streamlit run frontend/app.py
```

---

## API Endpoints

### `POST /analyze`
Analyze skill gap between a resume and job description.

**Request body:**
```json
{
  "resume_text": "...",
  "job_description": "...",
  "required_skills": ["Python", "Docker"],
  "target_role": "Backend Engineer"
}
```

**Response:**
```json
{
  "missing_skills": ["Docker", "AWS"],
  "matched_skills": ["Python"],
  "match_score": 0.33,
  "summary": "You match 33% of required skills..."
}
```

### `GET /roadmap?target_role=...&missing_skills=Docker,AWS`
Returns a step-by-step learning roadmap.

### `GET /jobs?category=backend&search=python`
Returns filtered job descriptions from the local dataset.

---

### 3. Basic Quality: Tests + Validation

**Input Validation:**
- `analyze.py`: Validates non-empty resume (400 error if empty)
- `interview.py`: Validates skills list and messages exist
- All inputs use Pydantic models for type safety

**Test Coverage (9 tests):**

| Test File | Test Name | Coverage |
|-----------|-----------|----------|
| `test_happy_path.py` | `test_analyze_happy_path` | Full gap analysis flow |
| `test_happy_path.py` | `test_jobs_returns_list` | Jobs endpoint returns data |
| `test_happy_path.py` | `test_jobs_filter_by_category` | Category filter works |
| `test_happy_path.py` | `test_roadmap_returns_steps` | Roadmap generation |
| `test_edge_cases.py` | `test_analyze_empty_resume` | 400 error on empty input |
| `test_edge_cases.py` | `test_analyze_no_matching_skills` | 0% match score handled |
| `test_edge_cases.py` | `test_analyze_ai_down_uses_fallback` | **AI fallback works** |
| `test_edge_cases.py` | `test_roadmap_empty_skills` | Empty roadmap handled |
| `test_edge_cases.py` | `test_jobs_search` | Search filter works |

### 4. Data Safety (Synthetic Data Only)

- `data/job_descriptions.json` — 20 synthetic JDs across 10 categories
- `data/sample_resume_*.txt` — 3 synthetic resumes (CS grad, career switcher, cybersecurity)
- `backend/fallback/skill_taxonomy.json` — Master skill list for fallback extraction
- No live scraping; all data checked into repo

### 5. Security

- API keys stored in `.env` (not committed)
- `.env.example` provided as template
- No hardcoded credentials
- CORS configured for local development

---

## Running Tests

```bash
pytest backend/tests/ -v
```

Tests cover:
- Happy path: valid resume → full analysis flow
- Edge cases: empty input, no skill matches, AI provider down (fallback), empty roadmap

---

## Fallback Mode

When no AI API key is configured (or the API is unavailable), SkillBridge falls back to:
- **Skill extraction**: regex keyword matching against `skill_taxonomy.json`
- **Gap analysis**: set-difference between resume skills and JD required skills
- **Roadmap**: static resource links from a curated map

---

## Sample Data

| File | Description |
|---|---|
| `data/sample_resume_1.txt` | Junior CS graduate |
| `data/sample_resume_2.txt` | Career switcher (marketing → data) |
| `data/sample_resume_3.txt` | Cybersecurity professional |
| `data/job_descriptions.json` | 20 synthetic JDs across 10 categories |

---

## Tech Stack

- **Backend**: FastAPI, Pydantic v2, Python 3.11+
- **AI**: OpenAI GPT-4o-mini / Anthropic Claude (with rule-based fallback)
- **Frontend**: Streamlit
- **Testing**: pytest, pytest-asyncio, httpx

---

## Project Structure

```
skill-bridge/
├── backend/
│   ├── main.py              # FastAPI app entry point
│   ├── config.py            # Pydantic settings (.env loader)
│   ├── routers/
│   │   ├── analyze.py       # POST /analyze — gap analysis endpoint
│   │   ├── roadmap.py       # GET /roadmap — learning roadmap endpoint
│   │   ├── jobs.py          # GET /jobs — job browser endpoint
│   │   └── interview.py     # POST /interview — mock interview endpoints
│   ├── services/
│   │   ├── ai_client.py     # Unified AI client (OpenRouter/Gemini/Anthropic)
│   │   ├── gap_analyzer.py  # AI + fallback gap analysis
│   │   ├── roadmap_builder.py # AI + fallback roadmap generation
│   │   ├── interview_generator.py # AI + fallback interview questions
│   │   ├── resume_parser.py # Text extraction
│   │   └── file_parser.py   # PDF/DOCX text extraction
│   ├── fallback/
│   │   ├── skill_matcher.py # Rule-based skill extraction (fallback)
│   │   └── skill_taxonomy.json # Master skills list
│   ├── models/
│   │   ├── analysis.py      # Pydantic models for API responses
│   │   ├── job.py           # Job description model
│   │   └── resume.py        # Resume model
│   └── tests/
│       ├── test_happy_path.py   # 4 happy path tests
│       └── test_edge_cases.py   # 5 edge case tests (including AI fallback)
├── data/
│   ├── job_descriptions.json    # 20 synthetic JDs
│   ├── sample_resume_1.txt      # Junior CS grad
│   ├── sample_resume_2.txt      # Career switcher
│   └── sample_resume_3.txt      # Cybersecurity pro
├── frontend/
│   └── app.py               # Streamlit UI
├── .env.example             # Template for API keys
├── requirements.txt         # Python dependencies
├── DESIGN.md                # Architecture and design decisions
└── README.md                # This file
```

---

## Design Process & Tradeoffs

### Why FastAPI + Streamlit?

**FastAPI** was chosen for:
- Native async support (needed for AI API calls)
- Automatic OpenAPI documentation
- Pydantic integration for type safety
- Minimal boilerplate

**Streamlit** was chosen for:
- Rapid prototyping (single Python file for UI)
- Built-in components for tables, progress bars, file upload
- No frontend framework complexity

**Tradeoff:** Streamlit is less customizable than React/Vue, but enabled building a functional UI in hours rather than days.

### Why Multiple AI Providers?

Supporting OpenRouter, Gemini, Anthropic, and Ollama provides:
- **Resilience**: If one provider is down, users can switch
- **Cost optimization**: Users choose cheapest option
- **Privacy**: Ollama allows local LLM execution

**Tradeoff:** More complex `ai_client.py` with multiple code paths, but worth it for flexibility.

### Why Synthetic Data?

- **Legal safety**: No scraping terms-of-service issues
- **Demo reliability**: Data always available, no network dependencies
- **Privacy**: No real personal data in repo

**Tradeoff:** Smaller dataset than live job boards, but sufficient for prototype validation.

### Key Technical Decisions

1. **Stateless API**: No database simplifies deployment, but means no user history persistence
2. **Regex fallback**: Simple but effective; works 100% offline
3. **Pydantic models**: Strict validation catches bugs early, but requires maintaining parallel models

### What I'd Do Differently

With more time:
- Add PostgreSQL for user accounts and saved analyses
- Implement PDF parsing for resume uploads (partially done)
- Add caching layer for AI responses
- Create React frontend for richer interactions
- Integrate with real job APIs (LinkedIn, Indeed) with proper rate limiting
