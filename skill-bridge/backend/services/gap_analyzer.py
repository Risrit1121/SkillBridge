import json
from backend.services.ai_client import call_ai
from backend.fallback.skill_matcher import compute_gap

PROMPT_TEMPLATE = """
You are a senior career coach and resume reviewer. Analyze the candidate's profile and return a JSON object with these exact keys:

- missing_skills: list of skills the candidate lacks for the role
- matched_skills: list of skills they already have
- match_score: float 0-1
- summary: 2-sentence plain-English summary of fit
- certifications: list of 3-5 specific certifications (with issuer) to fill the skill gaps, e.g. "AWS Certified Solutions Architect – AWS"
- resume_positives: list of 3 specific strengths observed in the resume
- resume_improvements: list of 3 specific, actionable improvements for the resume

Candidate skills: {resume_skills}
Resume text excerpt: {resume_text}
Job required skills: {jd_skills}
Target role: {role}

Respond ONLY with valid JSON.
"""

CERT_MAP = {
    "AWS": "AWS Certified Cloud Practitioner – AWS",
    "Kubernetes": "Certified Kubernetes Administrator (CKA) – CNCF",
    "Docker": "Docker Certified Associate – Docker",
    "Python": "PCEP – Certified Entry-Level Python Programmer – Python Institute",
    "Machine Learning": "Machine Learning Specialization – Coursera (DeepLearning.AI)",
    "SQL": "Google Data Analytics Certificate – Google",
    "React": "Meta Front-End Developer Certificate – Meta",
    "FastAPI": "Python Web Development with FastAPI – Udemy",
    "Terraform": "HashiCorp Certified: Terraform Associate – HashiCorp",
    "Security": "CompTIA Security+ – CompTIA",
    "Penetration Testing": "CEH – Certified Ethical Hacker – EC-Council",
    "Azure": "Microsoft Azure Fundamentals (AZ-900) – Microsoft",
    "GCP": "Google Cloud Associate Cloud Engineer – Google",
    "Scrum": "Professional Scrum Master I (PSM I) – Scrum.org",
}

async def analyze_gap(resume_skills: list[str], jd_skills: list[str], jd_text: str,
                      resume_text: str = "", target_role: str = "Software Engineer") -> dict:
    try:
        prompt = PROMPT_TEMPLATE.format(
            resume_skills=resume_skills,
            resume_text=resume_text[:800],
            jd_skills=jd_skills,
            role=target_role,
        )
        raw = await call_ai(prompt)
        raw = raw.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
        return json.loads(raw)
    except Exception:
        gap = compute_gap(resume_skills, jd_skills)
        score = gap["score"]
        certs = [CERT_MAP[s] for s in gap["missing"] if s in CERT_MAP][:4]
        return {
            "missing_skills": gap["missing"],
            "matched_skills": gap["matched"],
            "match_score": score,
            "summary": (
                f"You match {int(score*100)}% of the required skills. "
                f"Focus on acquiring: {', '.join(gap['missing'][:3]) or 'no major gaps found'}."
            ),
            "certifications": certs or ["AWS Certified Cloud Practitioner – AWS",
                                         "Google Data Analytics Certificate – Google"],
            "resume_positives": [
                "Demonstrates hands-on project experience.",
                "Shows relevant technical skills for the role.",
                "Includes measurable contributions.",
            ],
            "resume_improvements": [
                "Add quantified impact to each bullet (e.g. 'reduced latency by 30%').",
                "Include a concise professional summary at the top.",
                "Tailor skills section to match the target role's keywords.",
            ],
        }
