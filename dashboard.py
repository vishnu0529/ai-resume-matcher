import time, json, requests, streamlit as st

API_BASE = "https://ai-resume-matcher-production-87f6.up.railway.app/api/v1"

st.set_page_config(page_title="AI Resume Matcher", page_icon="🎯", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&family=JetBrains+Mono:wght@400;500&display=swap');
*, body, [class*="css"] { font-family: 'Inter', sans-serif !important; }
.header-dark { background: #0f172a; border-radius: 14px; padding: 1.75rem 2rem; margin-bottom: 1.25rem; border: 1px solid rgba(255,255,255,0.06); }
.header-dark h1 { color: #f8fafc; font-size: 1.6rem; font-weight: 600; margin: 0 0 4px; letter-spacing: -0.3px; }
.header-dark p { color: #94a3b8; font-size: 0.85rem; margin: 0; }
.hbadge { display: inline-block; padding: 2px 9px; border-radius: 20px; font-size: 11px; font-weight: 500; margin-right: 5px; font-family: 'JetBrains Mono', monospace; }
.hb-blue { background: #1e3a5f; color: #93c5fd; border: 1px solid #1d4ed8; }
.hb-green { background: #052e16; color: #86efac; border: 1px solid #166534; }
.hb-purple { background: #2e1065; color: #d8b4fe; border: 1px solid #7e22ce; }
.score-hero { background: #0f172a; border-radius: 14px; padding: 1.5rem; border: 1px solid rgba(255,255,255,0.06); }
.score-num { font-size: 3.5rem; font-weight: 600; line-height: 1; font-family: 'JetBrains Mono', monospace; }
.dark-mini { background: rgba(255,255,255,0.04); border-radius: 8px; padding: 10px 14px; margin-bottom: 6px; }
.dark-mini-label { font-size: 10px; color: #64748b; text-transform: uppercase; letter-spacing: 0.07em; margin: 0 0 3px; }
.dark-mini-val { font-size: 1.1rem; font-weight: 500; font-family: 'JetBrains Mono', monospace; }
.dark-bar { background: rgba(255,255,255,0.1); border-radius: 3px; height: 4px; margin-top: 5px; overflow: hidden; }
.sec-label { font-size: 10px; font-weight: 500; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.07em; margin: 0 0 10px; }
.pill { display: inline-block; padding: 3px 10px; border-radius: 20px; font-size: 11px; font-weight: 500; margin: 2px; }
.pill-green { background: #f0fdf4; color: #15803d; border: 1px solid #bbf7d0; }
.pill-blue { background: #eff6ff; color: #1d4ed8; border: 1px solid #bfdbfe; font-family: 'JetBrains Mono', monospace; font-size: 10px; }
.pill-red { background: #fff1f2; color: #be123c; border: 1px solid #fecdd3; }
.pill-amber { background: #fffbeb; color: #b45309; border: 1px solid #fde68a; }
.tip { border-left: 2px solid #6366f1; border-radius: 0 8px 8px 0; padding: 8px 12px; margin-bottom: 6px; font-size: 0.85rem; color: #334155; background: #fafafa; }
.qw { border-left: 2px solid #22c55e; border-radius: 0 8px 8px 0; padding: 8px 12px; margin-bottom: 6px; font-size: 0.85rem; color: #14532d; background: #f0fdf4; }
.chat-u { background: #1e3a5f; color: #e0f2fe; padding: 10px 14px; border-radius: 10px; margin: 6px 0 6px 2rem; font-size: 0.85rem; line-height: 1.5; }
.chat-a { background: #f8fafc; color: #1e293b; padding: 10px 14px; border-radius: 10px; margin: 6px 2rem 6px 0; font-size: 0.85rem; line-height: 1.5; border: 1px solid #e2e8f0; }
.step-dot { background: #6366f1; color: white; border-radius: 50%; width: 22px; height: 22px; display: inline-flex; align-items: center; justify-content: center; font-size: 11px; font-weight: 600; margin-right: 8px; flex-shrink: 0; }
</style>
""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("### Settings")
    use_agent = st.toggle("4-step agentic pipeline", value=True)
    st.caption("Skill extraction → gap scoring → content → strategy")
    st.divider()
    st.markdown("### Pipeline")
    for n, t, d in [("1","Skill extractor","Pulls skills from both docs"),("2","Gap analyser","Scores with breakdown"),("3","Content generator","Summary + cover letter"),("4","Strategist","ATS keywords + plan")]:
        st.markdown(f'<div style="display:flex;align-items:flex-start;margin-bottom:10px;"><span class="step-dot">{n}</span><div><div style="font-weight:500;font-size:0.82rem;color:#1e293b;">{t}</div><div style="font-size:0.75rem;color:#64748b;">{d}</div></div></div>', unsafe_allow_html=True)
    st.divider()
    st.markdown("[GitHub](https://github.com/vishnu0529/ai-resume-matcher) · [Live API](https://ai-resume-matcher-production-87f6.up.railway.app/docs) · v2.0")

st.markdown("""
<div class="header-dark">
<div style="display:flex;align-items:flex-start;justify-content:space-between;">
<div>
<h1>🎯 AI Resume Matcher</h1>
<p>Agentic LLM pipeline · 4-step analysis · Real-time career coaching</p>
<div style="margin-top:10px;">
<span class="hbadge hb-blue">Gemini 2.5 Flash</span>
<span class="hbadge hb-green">FastAPI · Railway</span>
<span class="hbadge hb-purple">Agentic Pipeline</span>
</div>
</div>
</div>
</div>
""", unsafe_allow_html=True)

c1, c2 = st.columns(2, gap="large")
with c1:
    st.markdown("#### Your resume")
    rf = st.file_uploader("Upload", type=["pdf","txt"], label_visibility="collapsed")
    rt = st.text_area("Or paste text", height=160, placeholder="Paste resume here...")
with c2:
    st.markdown("#### Job description")
    jd = st.text_area("Paste job description", height=210, placeholder="Paste full job posting here...", label_visibility="visible")

st.divider()
btn = st.button("Analyse with agentic pipeline" if use_agent else "Quick analyse", type="primary", use_container_width=True)

if btn:
    if not jd.strip(): st.error("Please paste a job description."); st.stop()
    if not rf and not rt.strip(): st.error("Please upload a resume or paste text."); st.stop()
    with st.spinner("Running 4-step pipeline... (~25s)"):
        t0 = time.time()
        try:
            if rf:
                resp = requests.post(f"{API_BASE}/match", files={"resume":(rf.name,rf.getvalue(),rf.type)}, data={"job_description":jd,"use_agent":str(use_agent).lower()}, timeout=120)
            else:
                resp = requests.post(f"{API_BASE}/match", data={"job_description":jd,"resume_text":rt,"use_agent":str(use_agent).lower()}, timeout=120)
        except requests.ConnectionError:
            st.error("Cannot reach API - is uvicorn running?"); st.stop()
    elapsed = time.time() - t0
    if not resp.ok: st.error(f"API error {resp.status_code}: {resp.json().get('detail','')}"); st.stop()
    r = resp.json()
    st.session_state["analysis"] = r
    st.session_state["elapsed"] = elapsed
    st.session_state["chat_history"] = []

if "analysis" in st.session_state:
    r = st.session_state["analysis"]
    elapsed = st.session_state.get("elapsed", 0)
    score = r["match_score"]
    grade = r["grade"]
    sc = "#4ade80" if score>=70 else "#fb923c" if score>=50 else "#f87171"
    gl = {"A":"Strong match","B":"Good match","C":"Moderate match","D":"Weak match","F":"Poor match"}.get(grade,"")

    st.divider()
    sh1, sh2 = st.columns([1, 2], gap="large")
    with sh1:
        bd = r.get("score_breakdown", {})
        rows = ""
        for lbl, key, col in [("Technical","technical_skills","#3b82f6"),("Experience","experience_level","#22c55e"),("Domain","domain_fit","#f59e0b"),("Soft skills","soft_skills","#94a3b8")]:
            v = bd.get(key, 0)
            rows += f'<div class="dark-mini"><div class="dark-mini-label">{lbl}</div><div class="dark-mini-val" style="color:{col};">{v}<span style="font-size:11px;color:#475569;">/100</span></div><div class="dark-bar"><div style="width:{v}%;height:100%;background:{col};border-radius:3px;"></div></div></div>'
        st.markdown(f'<div class="score-hero"><div class="score-num" style="color:{sc};">{score}</div><div style="font-size:0.95rem;color:#94a3b8;font-weight:500;margin:4px 0 1rem;">Grade {grade} · {gl}</div>{rows}</div>', unsafe_allow_html=True)
    with sh2:
        m1,m2,m3,m4 = st.columns(4)
        m1.metric("Matched", len(r.get("matched_skills",[])))
        m2.metric("Gaps", len(r.get("missing_skills",[])))
        m3.metric("ATS keys", len(r.get("ats_keywords",[])))
        sm = r.get("seniority_match","")
        m4.metric("Seniority", {"good":"Match","under":"Under","over":"Over"}.get(sm,"--"))
        if r.get("timeline"): st.info(f"**Time to close gap:** {r['timeline']}")
        if r.get("linkedin_headline"):
            st.markdown("**LinkedIn headline:**")
            st.code(r["linkedin_headline"], language=None)

    st.progress(score/100)
    st.divider()

    t1,t2,t3,t4,t5,t6 = st.tabs(["Skills","Content","ATS & Strategy","Plan","Roles","Chat"])

    with t1:
        ca,cb = st.columns(2, gap="large")
        with ca:
            st.markdown('<p class="sec-label">Matched skills</p>', unsafe_allow_html=True)
            st.markdown('<div style="line-height:2.2;">'+"".join([f'<span class="pill pill-green">{s}</span>' for s in r.get("matched_skills",[])])+'</div>', unsafe_allow_html=True)
            st.markdown('<p class="sec-label" style="margin-top:1rem;">Strengths</p>', unsafe_allow_html=True)
            for s in r.get("strengths",[]): st.markdown(f'<div class="qw">+ {s}</div>', unsafe_allow_html=True)
        with cb:
            st.markdown('<p class="sec-label">Skill gaps</p>', unsafe_allow_html=True)
            for g in r.get("missing_skills",[]):
                lbl = "Critical" if g["importance"]=="critical" else "Nice to have"
                with st.expander(f"{lbl} - {g['skill']}"): st.write(g["how_to_acquire"])
            st.markdown('<p class="sec-label" style="margin-top:1rem;">Weaknesses</p>', unsafe_allow_html=True)
            for w in r.get("weaknesses",[]): st.markdown(f'<div class="tip">- {w}</div>', unsafe_allow_html=True)

    with t2:
        st.markdown('<p class="sec-label">Tailored resume summary</p>', unsafe_allow_html=True)
        st.info(r.get("tailored_summary",""))
        if r.get("key_selling_points"):
            st.markdown('<p class="sec-label" style="margin-top:1rem;">Key selling points</p>', unsafe_allow_html=True)
            for p in r["key_selling_points"]: st.markdown(f'<div class="qw">+ {p}</div>', unsafe_allow_html=True)
        st.markdown('<p class="sec-label" style="margin-top:1rem;">Cover letter opener</p>', unsafe_allow_html=True)
        st.text_area("", value=r.get("cover_letter_snippet",""), height=180, disabled=True, label_visibility="collapsed")

    with t3:
        st.markdown('<p class="sec-label">ATS keywords - add these to your resume</p>', unsafe_allow_html=True)
        st.markdown('<div style="line-height:2.4;">'+"".join([f'<span class="pill pill-blue">{k}</span>' for k in r.get("ats_keywords",[])])+'</div>', unsafe_allow_html=True)
        if r.get("quick_wins"):
            st.markdown('<p class="sec-label" style="margin-top:1.25rem;">Quick wins - do today</p>', unsafe_allow_html=True)
            for w in r["quick_wins"]: st.markdown(f'<div class="qw">+ {w}</div>', unsafe_allow_html=True)

    with t4:
        st.markdown('<p class="sec-label">Prioritised improvement plan</p>', unsafe_allow_html=True)
        for i,tip in enumerate(r.get("improvement_tips",[]),1):
            st.markdown(f'<div class="tip"><span style="font-weight:600;color:#6366f1;">#{i}</span> {tip}</div>', unsafe_allow_html=True)

    with t5:
        st.markdown('<p class="sec-label">Roles matching your actual level</p>', unsafe_allow_html=True)
        cols = st.columns(3)
        for i,role in enumerate(r.get("recommended_roles",[])):
            cols[i%3].markdown(f'<div style="background:#f8fafc;border:1px solid #e2e8f0;border-radius:10px;padding:10px;margin-bottom:8px;text-align:center;font-size:0.85rem;font-weight:500;color:#1e293b;">{role}</div>', unsafe_allow_html=True)

    with t6:
        st.markdown('<p class="sec-label">Ask your AI career coach</p>', unsafe_allow_html=True)
        if "chat_history" not in st.session_state: st.session_state["chat_history"] = []
        for msg in st.session_state["chat_history"]:
            css = "chat-u" if msg["role"]=="user" else "chat-a"
            icon = "You" if msg["role"]=="user" else "AI Coach"
            st.markdown(f'<div class="{css}"><div style="font-size:10px;opacity:0.6;margin-bottom:3px;">{icon}</div>{msg["content"]}</div>', unsafe_allow_html=True)
        qc = st.columns(3)
        for i,q in enumerate(["Why is my score low?","What should I learn first?","Rewrite summary more senior"]):
            if qc[i].button(q, key=f"qq{i}"): st.session_state["pending_question"]=q
        qi = st.text_input("Ask anything...", placeholder="e.g. How do I address the TensorFlow gap?")
        ab = st.button("Ask AI Coach", type="primary")
        fq = st.session_state.get("pending_question","") or (qi if ab else "")
        if fq and st.session_state.get("analysis"):
            st.session_state["pending_question"]=""
            st.session_state["chat_history"].append({"role":"user","content":fq})
            with st.spinner("Thinking..."):
                try:
                    cr = requests.post(f"{API_BASE}/chat", json={"question":fq,"analysis_context":st.session_state["analysis"]}, timeout=30)
                    ans = cr.json()["answer"] if cr.ok else "Sorry, error."
                except: ans = "Connection error."
            st.session_state["chat_history"].append({"role":"ai","content":ans})
            st.rerun()

    st.divider()
    st.caption(f"Gemini 2.5 Flash · Inter font · Agentic pipeline · v2.1 · {elapsed:.1f}s")

else:
    st.markdown('<div style="text-align:center;padding:3rem 0;"><div style="font-size:2.5rem;margin-bottom:0.75rem;">🎯</div><div style="font-size:1rem;font-weight:500;color:#1e293b;">Ready to analyse</div><div style="font-size:0.85rem;color:#94a3b8;margin-top:4px;">Upload your resume and paste a job description above</div></div>', unsafe_allow_html=True)