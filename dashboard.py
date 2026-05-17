import time
import json
import requests
import streamlit as st

API_BASE = "http://localhost:8000/api/v1"

st.set_page_config(page_title="AI Resume Matcher", page_icon="🎯", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600&family=DM+Mono:wght@400;500&display=swap');
html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
.main-header { background: linear-gradient(135deg, #0f172a 0%, #1e3a5f 50%, #0f172a 100%); padding: 2.5rem 2rem; border-radius: 16px; margin-bottom: 2rem; border: 1px solid rgba(255,255,255,0.08); }
.main-header h1 { color: #f8fafc; font-size: 2.2rem; font-weight: 600; margin: 0 0 0.5rem 0; }
.main-header p { color: #94a3b8; font-size: 1rem; margin: 0; }
.badge { display: inline-block; padding: 0.2rem 0.7rem; border-radius: 20px; font-size: 0.72rem; font-weight: 500; margin-right: 0.4rem; font-family: 'DM Mono', monospace; }
.badge-blue { background: #1e3a5f; color: #60a5fa; border: 1px solid #1d4ed8; }
.badge-green { background: #052e16; color: #4ade80; border: 1px solid #166534; }
.badge-purple { background: #2e1065; color: #c084fc; border: 1px solid #7e22ce; }
.score-card { background: #0f172a; border: 1px solid rgba(255,255,255,0.08); border-radius: 16px; padding: 2rem; text-align: center; color: white; }
.score-number { font-size: 4rem; font-weight: 600; line-height: 1; margin-bottom: 0.25rem; }
.score-grade { font-size: 1.5rem; font-weight: 500; opacity: 0.7; }
.metric-card { background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 12px; padding: 1.2rem; margin-bottom: 0.75rem; }
.metric-card h4 { margin: 0 0 0.3rem 0; font-size: 0.8rem; color: #64748b; text-transform: uppercase; letter-spacing: 0.05em; }
.metric-card p { margin: 0; font-size: 1.4rem; font-weight: 600; color: #0f172a; }
.skill-pill { display: inline-block; padding: 0.3rem 0.8rem; border-radius: 20px; font-size: 0.8rem; font-weight: 500; margin: 0.2rem; }
.skill-matched { background: #d1fae5; color: #065f46; border: 1px solid #6ee7b7; }
.skill-ats { background: #ede9fe; color: #5b21b6; border: 1px solid #c4b5fd; }
.breakdown-bar { background: #e2e8f0; border-radius: 8px; height: 10px; margin: 4px 0 12px 0; overflow: hidden; }
.breakdown-fill { height: 100%; border-radius: 8px; }
.chat-message { padding: 0.8rem 1.1rem; border-radius: 12px; margin-bottom: 0.75rem; font-size: 0.92rem; line-height: 1.6; }
.chat-user { background: #1e3a5f; color: #e0f2fe; margin-left: 2rem; }
.chat-ai { background: #f1f5f9; color: #1e293b; margin-right: 2rem; border: 1px solid #e2e8f0; }
.tip-card { background: #fafafa; border-left: 3px solid #6366f1; border-radius: 0 8px 8px 0; padding: 0.8rem 1rem; margin-bottom: 0.6rem; font-size: 0.9rem; color: #334155; }
.quick-win { background: #f0fdf4; border-left: 3px solid #22c55e; border-radius: 0 8px 8px 0; padding: 0.8rem 1rem; margin-bottom: 0.6rem; font-size: 0.9rem; color: #14532d; }
.step-indicator { background: #6366f1; color: white; border-radius: 50%; width: 28px; height: 28px; display: inline-flex; align-items: center; justify-content: center; font-size: 0.8rem; font-weight: 600; margin-right: 8px; }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="main-header">
    <h1>🎯 AI Resume Matcher</h1>
    <p>Agentic LLM pipeline · 4-step analysis · Real-time career coaching</p>
    <br/>
    <span class="badge badge-blue">Gemini 2.5 Flash</span>
    <span class="badge badge-green">FastAPI</span>
    <span class="badge badge-purple">Agentic Pipeline</span>
</div>
""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("### Pipeline Settings")
    use_agent = st.toggle("Agentic pipeline (4-step)", value=True, help="4 specialised LLM calls for deeper analysis")
    st.caption("Skill extraction → gap analysis → content generation → strategy")
    st.divider()
    st.markdown("### How it works")
    for num, title, desc in [("1","Skill Extractor","Pulls skills from resume + JD"),("2","Gap Analyser","Scores match with breakdown"),("3","Content Generator","Tailored summary + cover letter"),("4","Strategist","ATS keywords + improvement plan")]:
        st.markdown(f'<div style="display:flex;align-items:flex-start;margin-bottom:10px;"><span class="step-indicator">{num}</span><div><div style="font-weight:600;font-size:0.85rem;color:#1e293b;">{title}</div><div style="font-size:0.78rem;color:#64748b;">{desc}</div></div></div>', unsafe_allow_html=True)
    st.divider()
    st.markdown("[GitHub](https://github.com/vishnu0529/ai-resume-matcher) · v2.0.0")

col1, col2 = st.columns(2, gap="large")
with col1:
    st.markdown("#### 📄 Your Resume")
    resume_file = st.file_uploader("Upload resume", type=["pdf","txt"], label_visibility="collapsed")
    resume_text_input = st.text_area("Or paste resume text", height=180, placeholder="Paste your resume here…")
with col2:
    st.markdown("#### 💼 Job Description")
    jd_input = st.text_area("Paste the full job description", height=230, placeholder="Paste the complete job posting here…")

st.divider()
analyse_btn = st.button("🚀 Analyse with AI Agent" if use_agent else "🔍 Quick Analyse", type="primary", use_container_width=True)

if analyse_btn:
    if not jd_input.strip():
        st.error("Please paste a job description.")
        st.stop()
    if not resume_file and not resume_text_input.strip():
        st.error("Please upload a resume or paste resume text.")
        st.stop()

    with st.spinner("Running 4-step agentic pipeline… (~25 seconds)"):
        t0 = time.time()
        try:
            if resume_file:
                resp = requests.post(f"{API_BASE}/match", files={"resume": (resume_file.name, resume_file.getvalue(), resume_file.type)}, data={"job_description": jd_input, "use_agent": str(use_agent).lower()}, timeout=120)
            else:
                resp = requests.post(f"{API_BASE}/match", data={"job_description": jd_input, "resume_text": resume_text_input, "use_agent": str(use_agent).lower()}, timeout=120)
        except requests.ConnectionError:
            st.error("Cannot reach the API. Is uvicorn running?")
            st.stop()

    elapsed = time.time() - t0
    if not resp.ok:
        st.error(f"API error {resp.status_code}: {resp.json().get('detail', resp.text)}")
        st.stop()

    r = resp.json()
    st.session_state["analysis"] = r
    st.session_state["chat_history"] = []

    st.divider()
    score = r["match_score"]
    grade = r["grade"]
    score_color = "#22c55e" if score >= 70 else "#f59e0b" if score >= 50 else "#ef4444"
    grade_label = {"A":"Strong match","B":"Good match","C":"Moderate match","D":"Weak match","F":"Poor match"}.get(grade,"")

    h1, h2, h3, h4 = st.columns(4)
    with h1:
        st.markdown(f'<div class="score-card"><div class="score-number" style="color:{score_color};">{score}</div><div class="score-grade">Grade {grade}</div><div style="font-size:0.8rem;opacity:0.6;margin-top:0.3rem;">{grade_label}</div></div>', unsafe_allow_html=True)
    with h2:
        st.markdown(f'<div class="metric-card"><h4>Matched Skills</h4><p>{len(r.get("matched_skills",[]))}</p></div><div class="metric-card"><h4>Skill Gaps</h4><p>{len(r.get("missing_skills",[]))}</p></div>', unsafe_allow_html=True)
    with h3:
        bd = r.get("score_breakdown", {})
        if bd:
            st.markdown("**Score breakdown**")
            for label, key, color in [("Technical","technical_skills","#6366f1"),("Experience","experience_level","#06b6d4"),("Domain fit","domain_fit","#10b981"),("Soft skills","soft_skills","#f59e0b")]:
                val = bd.get(key, 0)
                st.markdown(f'<div style="display:flex;justify-content:space-between;font-size:0.8rem;color:#64748b;"><span>{label}</span><span style="font-weight:500;color:#1e293b;">{val}/100</span></div><div class="breakdown-bar"><div class="breakdown-fill" style="width:{val}%;background:{color};"></div></div>', unsafe_allow_html=True)
        else:
            st.metric("Analysis time", f"{elapsed:.1f}s")
    with h4:
        if r.get("seniority_match"):
            labels = {"good":("✅","Seniority match","#22c55e"),"under":("⚠️","Under-qualified","#f59e0b"),"over":("ℹ️","Over-qualified","#6366f1")}
            em, lbl, col = labels.get(r["seniority_match"], ("","","#64748b"))
            st.markdown(f'<div style="font-size:0.85rem;color:{col};font-weight:500;margin-bottom:1rem;">{em} {lbl}</div>', unsafe_allow_html=True)
        if r.get("timeline"):
            st.markdown(f'<div class="metric-card"><h4>Time to close gap</h4><p style="font-size:1rem;">{r["timeline"]}</p></div>', unsafe_allow_html=True)

    st.progress(score / 100)
    st.divider()

    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(["📊 Skills Analysis","✍️ Tailored Content","🔑 ATS & Strategy","📈 Improvement Plan","🔭 Similar Roles","💬 Chat with AI Coach"])

    with tab1:
        c1, c2 = st.columns(2, gap="large")
        with c1:
            st.markdown("##### Matched Skills")
            st.markdown('<div style="line-height:2.2;">' + "".join([f'<span class="skill-pill skill-matched">{s}</span>' for s in r.get("matched_skills",[])]) + '</div>', unsafe_allow_html=True)
            st.markdown("##### Strengths")
            for s in r.get("strengths",[]): st.markdown(f'<div class="quick-win">✓ {s}</div>', unsafe_allow_html=True)
        with c2:
            st.markdown("##### Skill Gaps")
            for gap in r.get("missing_skills",[]):
                label = "🔴 Critical" if gap["importance"]=="critical" else "🟡 Nice-to-have"
                with st.expander(f"{label} — {gap['skill']}"):
                    st.markdown(f"**How to acquire:** {gap['how_to_acquire']}")
            st.markdown("##### Weaknesses")
            for w in r.get("weaknesses",[]): st.markdown(f'<div class="tip-card">↳ {w}</div>', unsafe_allow_html=True)

    with tab2:
        if r.get("linkedin_headline"):
            st.markdown("##### LinkedIn Headline")
            st.code(r["linkedin_headline"], language=None)
        st.markdown("##### Tailored Resume Summary")
        st.info(r.get("tailored_summary",""))
        if r.get("key_selling_points"):
            st.markdown("##### Key Selling Points (for interviews)")
            for p in r["key_selling_points"]: st.markdown(f'<div class="quick-win">• {p}</div>', unsafe_allow_html=True)
        st.divider()
        st.markdown("##### Cover Letter Opener")
        st.text_area("", value=r.get("cover_letter_snippet",""), height=200, disabled=True, label_visibility="collapsed")

    with tab3:
        st.markdown("##### ATS Keywords — add these to your resume")
        st.caption("Exact phrases the ATS will scan for.")
        st.markdown('<div style="line-height:2.5;">' + "".join([f'<span class="skill-pill skill-ats">{kw}</span>' for kw in r.get("ats_keywords",[])]) + '</div>', unsafe_allow_html=True)
        if r.get("quick_wins"):
            st.divider()
            st.markdown("##### Quick Wins — do these today")
            for w in r["quick_wins"]: st.markdown(f'<div class="quick-win">⚡ {w}</div>', unsafe_allow_html=True)

    with tab4:
        st.markdown("##### Prioritised Improvement Plan")
        for i, tip in enumerate(r.get("improvement_tips",[]),1):
            st.markdown(f'<div class="tip-card"><span style="font-weight:600;color:#6366f1;">#{i}</span> {tip}</div>', unsafe_allow_html=True)

    with tab5:
        st.markdown("##### Roles that match your actual level")
        cols = st.columns(3)
        for i, role in enumerate(r.get("recommended_roles",[])):
            cols[i%3].markdown(f'<div style="background:#f8fafc;border:1px solid #e2e8f0;border-radius:10px;padding:0.8rem 1rem;margin-bottom:0.5rem;text-align:center;font-weight:500;color:#1e293b;font-size:0.9rem;">{role}</div>', unsafe_allow_html=True)

    with tab6:
        st.markdown("##### Ask your AI career coach")
        st.caption("'Why is my score low?' · 'Rewrite my summary' · 'What should I learn first?'")
        if "chat_history" not in st.session_state: st.session_state["chat_history"] = []
        for msg in st.session_state["chat_history"]:
            css = "chat-user" if msg["role"]=="user" else "chat-ai"
            icon = "You" if msg["role"]=="user" else "AI Coach"
            st.markdown(f'<div class="chat-message {css}"><div style="font-size:0.7rem;opacity:0.6;margin-bottom:4px;">{icon}</div>{msg["content"]}</div>', unsafe_allow_html=True)
        qcols = st.columns(3)
        for i, q in enumerate(["Why is my score low?","What should I learn first?","Rewrite my summary to be more senior"]):
            if qcols[i].button(q, key=f"q{i}"): st.session_state["pending_question"] = q
        question = st.text_input("Or ask your own question…", placeholder="e.g. How do I address the Docker gap?")
        ask_btn = st.button("Ask AI Coach", type="primary")
        final_q = st.session_state.get("pending_question","") or (question if ask_btn else "")
        if final_q and st.session_state.get("analysis"):
            st.session_state["pending_question"] = ""
            st.session_state["chat_history"].append({"role":"user","content":final_q})
            with st.spinner("Thinking…"):
                try:
                    cr = requests.post(f"{API_BASE}/chat", json={"question":final_q,"analysis_context":st.session_state["analysis"]}, timeout=30)
                    answer = cr.json()["answer"] if cr.ok else "Sorry, could not get a response."
                except: answer = "Connection error. Is the API running?"
            st.session_state["chat_history"].append({"role":"ai","content":answer})
            st.rerun()

    st.divider()
    st.caption(f"Gemini 2.5 Flash · Agentic pipeline · {elapsed:.1f}s · v2.0.0")

elif "analysis" not in st.session_state:
    st.markdown('<div style="text-align:center;padding:3rem 1rem;color:#94a3b8;"><div style="font-size:3rem;margin-bottom:1rem;">🎯</div><div style="font-size:1.1rem;font-weight:500;color:#1e293b;margin-bottom:0.5rem;">Ready to analyse your resume</div><div style="font-size:0.9rem;">Upload your resume and paste a job description above, then click Analyse</div></div>', unsafe_allow_html=True)