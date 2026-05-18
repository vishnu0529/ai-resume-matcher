# 🎯 AI Resume Matcher & Job Recommendation System

[![Python](https://img.shields.io/badge/Python-3.9%2B-3776AB?logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Gemini](https://img.shields.io/badge/Gemini-2.5%20Flash-4285F4?logo=google&logoColor=white)](https://ai.google.dev)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.39-FF4B4B?logo=streamlit&logoColor=white)](https://streamlit.io)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)
![Version](https://img.shields.io/badge/Version-2.0.0-blueviolet)
![Pipeline](https://img.shields.io/badge/Pipeline-Agentic%204--step-orange)

> **v2.0** — Agentic 4-step LLM pipeline · AI chat coach · Score breakdown by category
> 
> An intelligent recruitment assistant that runs a multi-agent analysis chain: skill extraction
> → gap scoring → content generation → strategy — then lets you ask follow-up questions in plain English.

---

## 📋 Table of Contents
- [Overview](#-overview)
- [Features](#-features)
- [Architecture](#-architecture)
- [Quick Start](#-quick-start)
- [Configuration](#-configuration)
- [API Reference](#-api-reference)
- [Project Structure](#-project-structure)
- [How It Works](#-how-it-works)
- [Running Tests](#-running-tests)
- [Deployment](#-deployment)
- [Roadmap](#-roadmap)

---

## 🧠 Overview

AI Resume Matcher is a full-stack AI application that acts as an intelligent recruitment assistant.
It combines **Google Gemini 2.5 Flash** with a **FastAPI** backend and **Streamlit** dashboard
to give candidates deep, actionable insights on how well their resume fits any job description.

Unlike simple keyword matchers, this system uses large language models to understand context,
nuance, and role-specific requirements — the same way a senior recruiter would.

**Built to demonstrate:**
- Production-grade FastAPI application design
- LLM prompt engineering and structured JSON response parsing
- Multi-provider LLM abstraction (Google Gemini + Anthropic Claude)
- PDF parsing and text processing pipelines
- Professional Streamlit dashboard UX
- Docker containerisation and CI/CD with GitHub Actions

---

## ✨ Features

| Feature | Description |
|---|---|
| 🧠 **LLM Deep Analysis** | Gemini 2.5 Flash reads both documents for nuanced, context-aware match reports |
| 📊 **Match Score and Grade** | 0-100 score with A-F grade, calibrated to real hiring bar |
| 🔍 **Skill Gap Analysis** | Separates critical from nice-to-have missing skills with acquisition advice |
| ✍️ **Tailored Resume Summary** | AI rewrites your summary specifically for the target role |
| 📬 **Cover Letter Opener** | Personalised two-paragraph cover letter intro, ready to paste |
| 🔑 **ATS Keyword Extraction** | Exact-match keywords from the JD to add to your resume |
| 🔭 **Similar Role Suggestions** | Discover adjacent job titles you are qualified for |
| 💪 **Strengths and Weaknesses** | Honest, specific assessment of your profile vs the role |
| 📈 **Improvement Plan** | Prioritised, actionable steps to close the gap |
| 🌐 **Dual LLM Support** | Switch between Google Gemini and Anthropic Claude via one env var |
| 📄 **PDF and TXT Support** | Upload resume as PDF or plain text |
| 🐳 **Docker Ready** | One-command local or production deployment |
| 🤖 **Agentic Pipeline** | 4-step LLM chain: extract → score → generate → strategise |
| 💬 **AI Chat Coach** | Ask follow-up questions about your analysis in plain English |
| 📊 **Score Breakdown** | Category scores: technical, experience, domain fit, soft skills |
| ⚡ **Quick Wins** | 3 things you can do today to improve your application |
| 🔗 **LinkedIn Headline** | AI-generated headline optimised for the target role |

---

## 🏗️ Architecture

### v2.0 Agentic Pipeline

```
Streamlit Dashboard v2 (localhost:8501)
         |
         |  POST /api/v1/match        POST /api/v1/chat
         |
FastAPI Backend (localhost:8000)
         |
   parser.py
   PDF/TXT extract
         |
   recruiter_agent.py  ◄── 4-step agentic chain
         |
         ├─ [1] Skill Extractor    → resume_skills, jd_required, seniority_level
         │
         ├─ [2] Gap Analyser       → match_score, grade, score_breakdown, strengths
         │        (sees Step 1 output)
         │
         ├─ [3] Content Generator  → tailored_summary, cover_letter, linkedin_headline
         │        (sees Steps 1-2 output)
         │
         └─ [4] Strategist         → ats_keywords, improvement_tips, quick_wins, timeline
                  (sees Steps 1-3 output)
                       |
                  llm_client.py
              ┌────────┴────────┐
        Google Gemini    Anthropic Claude
         2.5 Flash         3.5 Haiku
              └────────────────────────────────────► /api/v1/chat
                                                    (follow-up Q&A
                                                    with full context)
```

### Request Flow
1. User uploads PDF resume + pastes job description
2. `parser.py` extracts and cleans text
3. `recruiter_agent.py` runs 4 sequential LLM agents, each building on previous outputs
4. Pydantic validates the assembled response
5. Dashboard renders 6-tab UI — Skills, Content, ATS, Plan, Roles, Chat

---

## 🚀 Quick Start
---

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- Free Google AI Studio API key (https://aistudio.google.com) OR Anthropic API key

### 1. Clone
```
git clone https://github.com/vishnu0529/ai-resume-matcher.git
cd ai-resume-matcher
```

### 2. Virtual environment
```
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies
```
pip install -r requirements.txt
```

### 4. Configure
```
cp .env.example .env
# Edit .env and add your API key
```

### 5. Run

Terminal 1 - API:
```
python -m uvicorn app.main:app --reload
```

Terminal 2 - Dashboard:
```
streamlit run dashboard.py
```

Open http://localhost:8501 to use the app.
API docs available at http://localhost:8000/docs.

**🌐 Live API:** https://ai-resume-matcher-production-87f6.up.railway.app/docs

---

## ⚙️ Configuration

| Variable | Default | Description |
|---|---|---|
| LLM_PROVIDER | google | google or anthropic |
| LLM_MODEL | gemini-2.5-flash | Model name for chosen provider |
| GOOGLE_API_KEY | - | Google AI Studio key (free tier available) |
| ANTHROPIC_API_KEY | - | Anthropic Console key |
| MAX_RESUME_SIZE_MB | 5 | Max upload size |
| LOG_LEVEL | INFO | Logging verbosity |

**Getting a free Google API key:**
1. Go to https://aistudio.google.com
2. Sign in with Google → Get API Key → Create API key
3. Free tier: 1,500 requests/day, no credit card needed

---

## 🔌 API Reference

### GET /health
```
{ "status": "ok", "version": "1.0.0", "llm_provider": "google" }
```

### POST /api/v1/match

Request (multipart/form-data):

| Field | Type | Required |
|---|---|---|
| job_description | string | Yes |
| resume | file PDF or TXT | Yes (or resume_text) |
| resume_text | string | Yes (or resume file) |

Response:
```
{
  "match_score": 72,
  "grade": "B",
  "matched_skills": ["Python", "FastAPI", "LangChain", "RAG pipelines"],
  "missing_skills": [
    {
      "skill": "Docker",
      "importance": "critical",
      "how_to_acquire": "Dockerise your existing FastAPI projects"
    }
  ],
  "strengths": ["Strong LLM engineering fundamentals"],
  "weaknesses": ["No cloud deployment experience"],
  "tailored_summary": "AI Engineer with hands-on LLM experience...",
  "cover_letter_snippet": "My experience building RAG pipelines...",
  "recommended_roles": ["Junior AI Engineer", "LLM Engineer"],
  "ats_keywords": ["LLM", "Python", "prompt engineering", "RAG"],
  "improvement_tips": ["Dockerise your projects and add to skills section"]
}
```

**Error codes:** 400 invalid input, 422 missing field, 500 LLM error

---

## 📁 Project Structure

```
ai-resume-matcher/
├── app/
│   ├── core/config.py          # Pydantic Settings - env vars
│   ├── models/schemas.py       # Request/response schemas
│   ├── routers/
│   │   ├── health.py           # GET /health
│   │   └── match.py            # POST /api/v1/match
│   ├── services/
│   │   ├── recruiter_agent.py  # 4-step agentic pipeline (v2)
│   │   ├── analyser.py         # Heuristic skill extraction
│   │   ├── llm_client.py       # Gemini / Claude abstraction
│   │   ├── matcher.py          # Single-shot LLM fallback
│   │   └── parser.py           # PDF/TXT extraction
│   └── main.py                 # FastAPI app factory
├── assets/
│   └── dashboard_screenshot.png
├── tests/test_api.py           # Full test suite
├── dashboard.py                # Streamlit frontend v2 with chat
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── .env.example
```

---

## 🔬 How It Works

### Agentic Pipeline (v2.0)
Instead of one monolithic prompt, the system runs 4 specialised LLM agents in sequence.
Each agent sees all previous outputs, enabling compound reasoning:

- Step 1 Skill Extractor: precision extraction with evidence citations from both documents
- Step 2 Gap Analyser: weighted scoring — technical 40%, experience 30%, domain 20%, soft 10%
- Step 3 Content Generator: personalised content grounded in actual resume facts, not hallucinations
- Step 4 Strategist: ATS keywords (exact JD strings), prioritised tips, quick wins, realistic timeline

### AI Chat Coach
After analysis, users ask follow-up questions via /api/v1/chat. The full analysis JSON
is passed as context with every question, so answers are specific and grounded.
Example questions: 'Why is my score low?', 'Rewrite my summary to sound more senior',
'What should I learn first to close the biggest gap?'

### Multi-Provider Abstraction
llm_client.py wraps both Google Gemini and Anthropic Claude behind a single interface.
Switching providers is one env var change — no code modifications needed.

### Pydantic Validation
Every LLM response is validated through Pydantic schemas before reaching the client,
catching malformed JSON, wrong types, and out-of-range scores automatically.

---

## 🧪 Running Tests

```
pip install pytest httpx
pytest tests/ -v
```

Covers: health check, input validation, PDF upload, text analysis, parser utilities,
skill extraction, and grade logic.

---

## 🐳 Deployment

### Docker
```
docker compose up --build
```

### Railway or Render (Free Cloud)
1. Push to GitHub
2. Connect repo to Railway (https://railway.app) or Render (https://render.com)
3. Add environment variables in dashboard
4. Deploy - done

---

## 🛣️ Roadmap

- [ ] Job board integration - analyse JDs directly from LinkedIn/Indeed URLs
- [ ] Batch analysis - compare one resume to multiple JDs at once
- [ ] Resume version history with diff view
- [ ] PDF export of full analysis report
- [ ] User accounts with saved sessions
- [ ] Browser extension - one-click analysis on any job posting

---

## 📄 License

MIT © Vishnu (https://github.com/vishnu0529)

---

Built with Google Gemini 2.5 Flash · FastAPI · Streamlit · Agentic LLM Pipeline

If this project helped you, consider giving it a star on GitHub ⭐
