import streamlit as st
import requests
import sys, os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

API_BASE = "http://localhost:8000"

st.set_page_config(page_title="SkillBridge", page_icon="🌉", layout="wide")
st.title("🌉 SkillBridge — AI Career Intelligence")

ROLES = [
    "Software Engineer",
    "Backend Engineer",
    "Frontend Developer",
    "Full Stack Engineer",
    "Data Engineer",
    "ML Engineer",
    "DevOps Engineer",
    "Cloud Architect",
    "Security Analyst",
    "Data Analyst",
    "Mobile Developer",
    "Scrum Master",
]
DIFFICULTY_COLOR = {"easy": "🟢", "medium": "🟡", "hard": "🔴"}
TYPE_ICON = {"conceptual": "💡", "practical": "🔧", "scenario": "🎯"}

# ── Sidebar: single resume upload, shared across all tabs ─────────────────────
with st.sidebar:
    st.header("📄 Your Resume")
    st.caption("Upload once — used across all tabs.")

    uploaded = st.file_uploader("Upload PDF / DOCX", type=["pdf", "docx", "doc"])
    if uploaded:
        from backend.services.file_parser import extract_text

        try:
            st.session_state["resume_text"] = extract_text(
                uploaded.read(), uploaded.name
            )
            st.success(f"✅ {uploaded.name}")
        except Exception as e:
            st.error(f"Parse error: {e}")

    pasted = st.text_area(
        "…or paste resume text",
        height=220,
        value=st.session_state.get("resume_text", ""),
        placeholder="Paste your resume here...",
    )
    if pasted.strip():
        st.session_state["resume_text"] = pasted

    if st.session_state.get("resume_text"):
        st.caption(f"✅ {len(st.session_state['resume_text'])} chars loaded")
    else:
        st.warning("No resume loaded yet.")


# ── helper ────────────────────────────────────────────────────────────────────
def get_skills(role: str) -> list[str]:
    resume = st.session_state.get("resume_text", "")
    if not resume.strip():
        return st.session_state.get("resume_skills", [])
    try:
        r = requests.post(
            f"{API_BASE}/analyze",
            json={
                "resume_text": resume,
                "job_description": "general",
                "required_skills": [],
                "target_role": role,
            },
        )
        return r.json().get("matched_skills", []) if r.ok else []
    except Exception:
        return st.session_state.get("resume_skills", [])


# ── Tabs ──────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs(
    ["📊 Gap Analysis", "🎤 Mock Interview", "🗺️ Roadmap", "💼 Browse Jobs"]
)

# ── Tab 1: Gap Analysis ───────────────────────────────────────────────────────
with tab1:
    st.subheader("Resume Gap Analysis")
    st.caption(
        "Pick a target role — AI benchmarks your resume against all matching job descriptions."
    )

    col_l, col_r = st.columns([2, 1])
    with col_l:
        target_role = st.selectbox("Target Role", ROLES, key="dash_role")
    with col_r:
        st.markdown("**How it works:**")
        st.markdown("- Aggregates skills from all matching JDs")
        st.markdown("- AI scores fit, finds gaps, suggests certs & resume tips")

    if st.button("🔍 Analyze My Profile", type="primary"):
        resume = st.session_state.get("resume_text", "")
        if not resume.strip():
            st.error("Upload or paste your resume in the sidebar first.")
        else:
            with st.spinner("Fetching job market data..."):
                try:
                    jds, seen_ids = [], set()
                    for word in [w for w in target_role.lower().split() if len(w) > 3]:
                        r = requests.get(f"{API_BASE}/jobs", params={"search": word})
                        if r.ok:
                            for j in r.json():
                                if j["id"] not in seen_ids:
                                    jds.append(j)
                                    seen_ids.add(j["id"])
                    if not jds:
                        r = requests.get(f"{API_BASE}/jobs")
                        if r.ok:
                            jds = r.json()
                except Exception as e:
                    st.error(f"Could not load jobs: {e}")
                    jds = []

            if not jds:
                st.warning("No job descriptions found. Try a different role.")
            else:
                all_skills, seen = [], set()
                for jd in jds:
                    for s in jd.get("required_skills", []):
                        if s not in seen:
                            all_skills.append(s)
                            seen.add(s)

                with st.spinner(f"Analyzing against {len(jds)} JDs..."):
                    try:
                        resp = requests.post(
                            f"{API_BASE}/analyze",
                            json={
                                "resume_text": resume,
                                "job_description": f"Aggregated from {len(jds)} JDs for {target_role}.",
                                "required_skills": all_skills,
                                "target_role": target_role,
                            },
                        )
                        resp.raise_for_status()
                        d = resp.json()

                        # metrics row
                        st.markdown("---")
                        m1, m2, m3 = st.columns(3)
                        m1.metric("Match Score", f"{int(d['match_score'] * 100)}%")
                        m2.metric("Skills You Have", len(d["matched_skills"]))
                        m3.metric("Skills to Gain", len(d["missing_skills"]))
                        st.progress(d["match_score"])
                        st.info(d["summary"])

                        # skills tables
                        col_a, col_b = st.columns(2)
                        with col_a:
                            st.markdown("#### ✅ Matched Skills")
                            st.table({"Skill": d["matched_skills"]})
                        with col_b:
                            st.markdown("#### ❌ Skill Gaps")
                            st.table({"Skill": d["missing_skills"]})

                        # certifications
                        if d.get("certifications"):
                            st.markdown("---")
                            st.markdown("#### 🎓 Recommended Certifications")
                            for c in d["certifications"]:
                                st.markdown(f"- {c}")

                        # resume feedback
                        st.markdown("---")
                        fb1, fb2 = st.columns(2)
                        with fb1:
                            st.markdown("#### 👍 Resume Strengths")
                            for p in d.get("resume_positives", []):
                                st.success(p)
                        with fb2:
                            st.markdown("#### 🔧 Resume Improvements")
                            for i in d.get("resume_improvements", []):
                                st.warning(i)

                        st.markdown("---")
                        st.caption(
                            f"Benchmarked against **{len(jds)} JDs** | Role: **{target_role}**"
                        )

                        st.session_state.update(
                            {
                                "resume_skills": d["matched_skills"],
                                "missing_skills": d["missing_skills"],
                                "target_role": target_role,
                            }
                        )
                    except Exception as e:
                        st.error(f"API error: {e}")

# ── Tab 2: Mock Interview ─────────────────────────────────────────────────────
with tab2:
    st.subheader("🎤 Mock Interview")
    iv_tab1, iv_tab2 = st.tabs(["📋 Question Bank", "🤖 AI Interview Coach"])

    # Sub-tab 1: Question Bank
    with iv_tab1:
        st.caption("AI generates targeted questions based on your resume skills.")
        iv_role_q = st.selectbox(
            "Target Role",
            ROLES,
            key="iv_role_q",
            index=(
                ROLES.index(st.session_state.get("target_role", "Software Engineer"))
                if st.session_state.get("target_role") in ROLES
                else 0
            ),
        )
        num_q = st.slider("Number of Questions", 4, 15, 8)

        if st.button("🎤 Generate Questions", type="primary", key="btn_gen_q"):
            if not st.session_state.get("resume_text", "").strip():
                st.error("Upload or paste your resume in the sidebar first.")
            else:
                with st.spinner("Extracting skills & generating questions..."):
                    skills = get_skills(iv_role_q)
                if not skills:
                    st.warning(
                        "No skills extracted. Add more technical keywords to your resume."
                    )
                else:
                    with st.spinner("Generating questions..."):
                        try:
                            r = requests.post(
                                f"{API_BASE}/interview",
                                json={
                                    "skills": skills,
                                    "target_role": iv_role_q,
                                    "num_questions": num_q,
                                },
                            )
                            r.raise_for_status()
                            questions = r.json().get("questions", [])
                            st.markdown(
                                f"#### {len(questions)} Questions for **{iv_role_q}**"
                            )
                            st.caption(f"Skills: {', '.join(skills)}")
                            st.markdown("---")
                            for i, q in enumerate(questions, 1):
                                diff, qtype = q.get("difficulty", "medium"), q.get(
                                    "type", "conceptual"
                                )
                                label = f"Q{i}. {DIFFICULTY_COLOR.get(diff,'🟡')} {TYPE_ICON.get(qtype,'💡')} {q['question']}"
                                with st.expander(
                                    label[:110] + "..." if len(label) > 110 else label
                                ):
                                    st.markdown(f"**{q['question']}**")
                                    st.caption(
                                        f"Skill: `{q.get('skill','')}` | Type: `{qtype}` | Difficulty: `{diff}`"
                                    )
                        except Exception as e:
                            st.error(f"API error: {e}")

    # Sub-tab 2: AI Interview Coach
    with iv_tab2:
        st.caption(
            "Agentic AI tool acts as your personal interview coach — asks resume-based questions, gives feedback, and scores you at the end."
        )

        # ── active session ──
        if st.session_state.get("iv_started"):
            iv_skills = st.session_state["iv_skills"]
            iv_role_active = st.session_state["iv_role"]
            messages = st.session_state["iv_messages"]

            col_info, col_reset = st.columns([4, 1])
            with col_info:
                st.caption(
                    f"Role: **{iv_role_active}** | Skills: {', '.join(iv_skills)}"
                )
            with col_reset:
                if st.button("🔄 Reset", key="btn_reset"):
                    st.session_state["iv_started"] = False
                    st.session_state["iv_messages"] = []
                    st.session_state["iv_skills"] = []
                    st.session_state["iv_role"] = ""
                    st.rerun()

            # fixed-height scrollable message area — keeps chat_input pinned below
            chat_box = st.container(height=420)
            with chat_box:
                for msg in messages:
                    with st.chat_message(
                        "assistant" if msg["role"] == "assistant" else "user"
                    ):
                        st.markdown(msg["content"])

            user_input = st.chat_input("Type your answer...")
            if user_input:
                messages.append({"role": "user", "content": user_input})
                # immediately show user msg inside the box on next rerun
                st.session_state["iv_messages"] = messages
                with st.spinner("Interviewer is thinking..."):
                    try:
                        r = requests.post(
                            f"{API_BASE}/interview/chat",
                            json={
                                "messages": messages,
                                "skills": iv_skills,
                                "target_role": iv_role_active,
                            },
                            timeout=60,
                        )
                        reply = (
                            r.json()["reply"]
                            if r.ok
                            else f"API error {r.status_code}: {r.text[:100]}"
                        )
                    except Exception as e:
                        reply = f"Connection error: {e}"
                messages.append({"role": "assistant", "content": reply})
                st.session_state["iv_messages"] = messages
                st.rerun()

        # ── setup screen (no active session) ──
        else:
            iv_role_c = st.selectbox(
                "Target Role",
                ROLES,
                key="iv_role_c",
                index=(
                    ROLES.index(
                        st.session_state.get("target_role", "Software Engineer")
                    )
                    if st.session_state.get("target_role") in ROLES
                    else 0
                ),
            )
            st.markdown(
                "The AI interviewer will greet you, ask role-specific questions based on your resume, provide feedback after each answer, and give a final score out of 10."
            )

            if st.button("🚀 Start Interview", type="primary", key="btn_start"):
                if not st.session_state.get("resume_text", "").strip():
                    st.error("Upload or paste your resume in the sidebar first.")
                else:
                    with st.spinner("Preparing interview..."):
                        skills = get_skills(iv_role_c)
                    if not skills:
                        st.warning("No skills extracted from resume.")
                    else:
                        with st.spinner(
                            "Interviewer is preparing the first question..."
                        ):
                            try:
                                r = requests.post(
                                    f"{API_BASE}/interview/chat",
                                    json={
                                        "messages": [
                                            {
                                                "role": "user",
                                                "content": "Hello, I'm ready to start.",
                                            }
                                        ],
                                        "skills": skills,
                                        "target_role": iv_role_c,
                                    },
                                    timeout=60,
                                )
                                opening = (
                                    r.json()["reply"]
                                    if r.ok
                                    else "Hello! Let's begin. Tell me about yourself."
                                )
                            except Exception:
                                opening = "Hello! Let's begin. Tell me about yourself."
                        st.session_state.update(
                            {
                                "iv_started": True,
                                "iv_skills": skills,
                                "iv_role": iv_role_c,
                                "iv_messages": [
                                    {"role": "assistant", "content": opening}
                                ],
                            }
                        )
                        st.rerun()

# ── Tab 3: Roadmap ────────────────────────────────────────────────────────────
with tab3:
    st.subheader("Learning Roadmap")
    role = st.selectbox(
        "Target Role",
        ROLES,
        key="rm_role",
        index=(
            ROLES.index(st.session_state.get("target_role", "Software Engineer"))
            if st.session_state.get("target_role") in ROLES
            else 0
        ),
    )
    missing_input = st.text_input(
        "Missing Skills (auto-filled from Gap Analysis)",
        value=", ".join(st.session_state.get("missing_skills", [])),
    )

    if st.button("Generate Roadmap", type="primary"):
        with st.spinner("Building roadmap..."):
            try:
                resp = requests.get(
                    f"{API_BASE}/roadmap",
                    params={
                        "target_role": role,
                        "missing_skills": missing_input,
                    },
                )
                resp.raise_for_status()
                data = resp.json()
                st.success(f"📅 Estimated time: **{data['total_weeks']} weeks**")
                for step in data["steps"]:
                    with st.expander(
                        f"Step {step['order']}: {step['skill']} — {step['duration_weeks']} weeks"
                    ):
                        st.markdown(f"[📚 Start Learning]({step['resource']})")
            except Exception as e:
                st.error(f"API error: {e}")

# ── Tab 4: Browse Jobs ────────────────────────────────────────────────────────
with tab4:
    st.subheader("Browse Job Descriptions")
    col1, col2 = st.columns(2)
    with col1:
        search = st.text_input("Search", placeholder="e.g. Python, React...")
    with col2:
        category = st.selectbox(
            "Category",
            [
                "",
                "backend",
                "frontend",
                "fullstack",
                "data",
                "ml",
                "devops",
                "security",
                "cloud",
                "mobile",
                "management",
            ],
        )
    try:
        resp = requests.get(
            f"{API_BASE}/jobs", params={"search": search, "category": category}
        )
        resp.raise_for_status()
        jobs = resp.json()
        st.caption(f"{len(jobs)} jobs found")
        for job in jobs:
            with st.expander(f"{job['title']} @ {job['company']}"):
                st.write(job["description"])
                st.write("**Required Skills:** " + ", ".join(job["required_skills"]))
    except Exception as e:
        st.error(f"Could not load jobs: {e}")
