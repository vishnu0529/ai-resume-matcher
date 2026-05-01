import anthropic
import json
import os
from dotenv import load_dotenv

from app.services.matcher import compute_match_score

load_dotenv()
client = anthropic.Anthropic()


def analyse(resume_text: str, job_text: str) -> dict:
    prompt = f"""You are an expert career coach and recruiter.

RESUME:
{resume_text[:3000]}

JOB DESCRIPTION:
{job_text[:2000]}

Analyse the match and respond ONLY with valid JSON (no markdown, no preamble):
{{
  "present_skills": ["skill1", "skill2"],
  "missing_skills": ["skill1", "skill2"],
  "strengths": ["strength 1", "strength 2", "strength 3"],
  "gaps": ["gap 1", "gap 2"],
  "interview_tips": ["tip 1", "tip 2", "tip 3"],
  "tailored_summary": "A 3-4 sentence professional summary rewritten specifically for this role"
}}"""

    try:
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1500,
            messages=[{"role": "user", "content": prompt}]
        )
        raw = response.content[0].text.strip()
        return json.loads(raw)
    except Exception:
        return _fallback_analyse(resume_text, job_text)


def tailor_resume(resume_text: str, job_text: str) -> str:
    prompt = f"""You are a professional resume writer.

Rewrite the resume below so it is highly tailored for the job description provided.
- Keep all factual information accurate
- Reorder and reword bullet points to match the job's priorities
- Use keywords from the job description naturally
- Keep the same overall structure

RESUME:
{resume_text[:3000]}

JOB DESCRIPTION:
{job_text[:2000]}

Return ONLY the rewritten resume text, no commentary."""

    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=2000,
        messages=[{"role": "user", "content": prompt}]
    )
    return response.content[0].text.strip()


def _fallback_analyse(resume_text: str, job_text: str) -> dict:
    keywords = [
        "Python", "FastAPI", "LLMs", "LLM integration", "vector databases",
        "RAG pipelines", "OpenAI", "Anthropic Claude", "NLP", "API design"
    ]
    lowered_resume = resume_text.lower()
    lowered_job = job_text.lower()

    present_skills = [k for k in keywords if k.lower() in lowered_resume and k.lower() in lowered_job]
    missing_skills = [k for k in keywords if k.lower() in lowered_job and k.lower() not in lowered_resume]

    strengths = []
    if "Python" in present_skills and "FastAPI" in present_skills:
        strengths.append("Strong backend development with Python and FastAPI.")
    if any(k in present_skills for k in ["NLP", "LLMs"]):
        strengths.append("Relevant experience with NLP and modern AI technologies.")
    if not strengths:
        strengths.append("Solid software engineering experience and technical foundation.")

    gaps = []
    if any(x in missing_skills for x in ["LLMs", "vector databases", "RAG pipelines"]):
        gaps.append("Missing explicit experience with generative AI and retrieval-augmented systems.")
    if not gaps:
        gaps.append("No major gaps identified from the provided text.")

    interview_tips = [
        "Highlight your backend API work and project outcomes.",
        "Emphasize any NLP or AI-related learning and deployments.",
        "Mention your ability to adopt vector search and LLM workflows quickly."
    ]

    tailored_summary = (
        "Experienced Python backend developer with strong FastAPI and API delivery skills, "
        "well-positioned for AI-engineering roles by emphasizing NLP and AI system readiness."
    )

    return {
        "present_skills": present_skills,
        "missing_skills": missing_skills,
        "strengths": strengths,
        "gaps": gaps,
        "interview_tips": interview_tips,
        "tailored_summary": tailored_summary,
    }


def analyze_match(resume_text: str, job_description: str) -> dict:
    return compute_match_score(resume_text, job_description)
