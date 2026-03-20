# SkillBridge — Design Documentation

## Architecture Overview

SkillBridge is a FastAPI + Streamlit application that helps job seekers identify skill gaps and create learning roadmaps.

```
┌─────────────────┐      HTTP       ┌─────────────────────────────────────────────┐
│  Streamlit UI   │ ◄─────────────► │  FastAPI Backend                            │
│  (frontend/)    │                 │  ├── /analyze   → Gap analysis              │
│                 │                 │  ├── /roadmap   → Learning roadmap          │
│                 │                 │  ├── /jobs      → Job browsing              │
│                 │                 │  └── /interview → Mock interview            │
└─────────────────┘                 │                                             │
                                    │  Services:                                  │
                                    │  ├── ai_client.py      → Multi-provider AI │
                                    │  ├── gap_analyzer.py   → Skill gap logic  │
                                    │  ├── roadmap_builder.py → Learning paths  │
                                    │  └── interview_generator.py → Questions   │
                                    │                                             │
                                    │  Fallback:                                  │
                                    │  └── skill_matcher.py  → Rule-based backup │
                                    └─────────────────────────────────────────────┘
```

## Tech Stack

| Layer | Technology | Purpose |
|-------|------------|---------|
| **Backend** | FastAPI | High-performance API framework |
| **Models** | Pydantic v2 | Request/response validation |
| **AI** | OpenRouter/Gemini/Anthropic | LLM for analysis & generation |
| **Fallback** | Regex + JSON | Rule-based skill extraction |
| **Frontend** | Streamlit | Rapid UI development |
| **Testing** | pytest + httpx | Async test coverage |

## Key Design Decisions

### 1. AI-First with Fallback
- **Decision**: Use LLM for intelligent analysis, but always provide rule-based fallback
- **Rationale**: Ensures 100% uptime even if AI providers fail or user has no API key
- **Implementation**: All AI calls wrapped in try/except; fallback uses `skill_taxonomy.json` + regex

### 2. Unified AI Client
- **Decision**: Single `ai_client.py` supporting multiple providers (OpenRouter, Gemini, Anthropic, Ollama)
- **Rationale**: Avoids vendor lock-in; users can choose cheapest/most available option
- **Configuration**: Via `.env` — `AI_PROVIDER` and `MODEL_NAME`

### 3. Synthetic Data Only
- **Decision**: Bundle job descriptions and resumes in repo instead of live scraping
- **Rationale**: Eliminates legal/compliance concerns; ensures reproducible demos
- **Tradeoff**: Smaller dataset (20 JDs vs thousands), but sufficient for prototype

### 4. Stateless API
- **Decision**: No database; all state in memory or client-side
- **Rationale**: Simplifies deployment; no migrations or connection management
- **Tradeoff**: Cannot persist user history; could add SQLite for future versions

## API Endpoints

| Endpoint | Method | Description | Request | Response |
|----------|--------|-------------|---------|----------|
| `/analyze` | POST | Compare resume to job | `resume_text`, `required_skills`, `target_role` | `missing_skills`, `match_score`, `summary` |
| `/roadmap` | GET | Generate learning path | `target_role`, `missing_skills` | `steps[]`, `total_weeks` |
| `/jobs` | GET | Browse job descriptions | `category`, `search` | `JobDescription[]` |
| `/interview` | POST | Generate interview Qs | `skills`, `target_role`, `num_questions` | `questions[]` |
| `/interview/chat` | POST | AI interview chat | `messages[]`, `skills` | `reply` |

## AI Capabilities

### Primary: Skill Gap Analysis (Extract + Categorize)
1. **Extract** skills from resume text using LLM
2. **Categorize** into "matched" vs "missing" compared to job requirements
3. **Summarize** fit with narrative explanation
4. **Recommend** certifications and resume improvements

### Secondary: Learning Roadmap (Forecast)
1. **Forecast** time to learn each missing skill
2. **Sequence** skills in optimal learning order
3. **Resource** links for each skill

### Tertiary: Mock Interview (Generate)
1. **Generate** questions based on resume skills
2. **Adapt** follow-up questions based on answers
3. **Score** candidate performance (1-10)

## Fallback Strategy

| Feature | AI Path | Fallback Path |
|---------|---------|---------------|
| Skill Extraction | LLM parses resume | Regex match against `skill_taxonomy.json` |
| Gap Analysis | LLM compares + summarizes | Set difference + template summary |
| Roadmap | LLM generates custom steps | Static resource mapping |
| Interview | LLM conversational chat | Canned questions by skill/role |

## Data Model

```python
SkillGap:
  - missing_skills: list[str]
  - matched_skills: list[str]
  - match_score: float (0-1)
  - summary: str
  - certifications: list[str]
  - resume_positives: list[str]
  - resume_improvements: list[str]

Roadmap:
  - target_role: str
  - steps: list[RoadmapStep]
  - total_weeks: int

RoadmapStep:
  - order: int
  - skill: str
  - resource: str (URL)
  - duration_weeks: int
```

## Future Enhancements

1. **Database Persistence**: PostgreSQL/SQLite for user profiles and analysis history
2. **Resume Upload**: PDF/DOCX parser (partially implemented in `file_parser.py`)
3. **Real Job Data**: Integration with LinkedIn/Indeed APIs (respecting rate limits)
4. **Progress Tracking**: Mark roadmap steps complete, update match score over time
5. **Job Application Tracker**: Log applications, interviews, offers
6. **Multi-language Support**: i18n for Spanish, Chinese markets
7. **ATS Optimization**: Score resume against ATS filters

## Security Considerations

- API keys stored in `.env` (never committed)
- CORS configured for local development only
- No PII stored in repository (all synthetic data)
- Input validation via Pydantic models
- No SQL injection risk (no database)

## Performance Notes

- AI calls are async to prevent blocking
- Skill taxonomy loaded once at startup
- Job descriptions cached in memory
- Frontend polls backend (could use WebSockets for chat)

---

Last updated: March 2026
