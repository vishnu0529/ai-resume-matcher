import logging
import json
from app.services.llm_client import call_llm, call_llm_json
from app.models.schemas import MatchResponse, SkillGap

logger = logging.getLogger(__name__)

SKILL_EXTRACTOR_PROMPT = """You are a precise technical skill extractor.
From the RESUME extract technical skills, soft skills, experience indicators, qualifications.
From the JOB DESCRIPTION extract required skills (critical) and nice-to-have skills.
Return ONLY valid JSON:
{
  "resume_skills": [{"skill": "string", "evidence": "string"}],
  "jd_required": [{"skill": "string", "importance": "critical"}],
  "jd_preferred": [{"skill": "string", "importance": "nice-to-have"}],
  "experience_required": "string",
  "seniority_level": "string"
}""".strip()

GAP_ANALYSER_PROMPT = """You are a senior recruitment consultant scoring candidate fit.
Score the match honestly 0-100: technical overlap 40%, experience 30%, domain fit 20%, soft skills 10%.
Be brutally honest. Junior candidate for senior role = 20-40.
Return ONLY valid JSON:
{
  "match_score": 0,
  "grade": "A",
  "matched_skills": ["string"],
  "missing_skills": [{"skill": "string", "importance": "critical", "how_to_acquire": "string"}],
  "strengths": ["string"],
  "weaknesses": ["string"],
  "seniority_match": "under",
  "score_breakdown": {"technical_skills": 0, "experience_level": 0, "domain_fit": 0, "soft_skills": 0}
}""".strip()

CONTENT_GEN_PROMPT = """You are an expert career coach and writer.
Write compelling personalised content. Do not invent experience.
Return ONLY valid JSON:
{
  "tailored_summary": "string",
  "cover_letter_snippet": "string",
  "linkedin_headline": "string",
  "key_selling_points": ["string"]
}""".strip()

STRATEGIST_PROMPT = """You are a strategic career advisor.
ATS keywords must be EXACT strings from the job description.
Return ONLY valid JSON:
{
  "ats_keywords": ["string"],
  "improvement_tips": ["string"],
  "recommended_roles": ["string"],
  "quick_wins": ["string"],
  "timeline": "string"
}""".strip()

CHAT_SYSTEM_PROMPT = """You are a helpful career coach AI. The user received an AI analysis
of their resume against a job description. Answer follow-up questions based on the analysis
context. Be specific, honest, and actionable. Keep answers concise.""".strip()


def _extract_skills(resume, jd):
    user = f"=== RESUME ===\n{resume}\n\n=== JOB DESCRIPTION ===\n{jd}"
    return call_llm_json(SKILL_EXTRACTOR_PROMPT, user, max_tokens=1500)

def _analyse_gap(resume, jd, skills_data):
    user = f"=== EXTRACTED SKILLS ===\n{json.dumps(skills_data, indent=2)}\n\n=== RESUME ===\n{resume[:2000]}\n\n=== JOB DESCRIPTION ===\n{jd[:2000]}"
    return call_llm_json(GAP_ANALYSER_PROMPT, user, max_tokens=1500)

def _generate_content(resume, jd, gap_data):
    user = f"=== GAP ANALYSIS ===\n{json.dumps(gap_data, indent=2)}\n\n=== RESUME ===\n{resume[:2000]}\n\n=== JOB DESCRIPTION ===\n{jd[:1500]}"
    return call_llm_json(CONTENT_GEN_PROMPT, user, max_tokens=1200)

def _build_strategy(gap_data, content_data, jd):
    user = f"=== GAP ANALYSIS ===\n{json.dumps(gap_data, indent=2)}\n\n=== CONTENT ===\n{json.dumps(content_data, indent=2)}\n\n=== JOB DESCRIPTION ===\n{jd[:2000]}"
    return call_llm_json(STRATEGIST_PROMPT, user, max_tokens=1200)

def _score_grade(score):
    if score >= 85: return "A"
    if score >= 70: return "B"
    if score >= 55: return "C"
    if score >= 40: return "D"
    return "F"

def run_agent(resume_text, jd_text):
    logger.info("Agent step 1/4: extracting skills...")
    skills = _extract_skills(resume_text, jd_text)
    logger.info("Agent step 2/4: analysing gap...")
    gap = _analyse_gap(resume_text, jd_text, skills)
    logger.info("Agent step 3/4: generating content...")
    content = _generate_content(resume_text, jd_text, gap)
    logger.info("Agent step 4/4: building strategy...")
    strategy = _build_strategy(gap, content, jd_text)

    score = int(gap.get("match_score", 0))
    missing_skills = [
        SkillGap(skill=g.get("skill",""), importance=g.get("importance","nice-to-have"), how_to_acquire=g.get("how_to_acquire",""))
        for g in gap.get("missing_skills", [])
    ]
    result = MatchResponse(
        match_score=score, grade=gap.get("grade") or _score_grade(score),
        matched_skills=gap.get("matched_skills", []), missing_skills=missing_skills,
        strengths=gap.get("strengths", []), weaknesses=gap.get("weaknesses", []),
        tailored_summary=content.get("tailored_summary", ""),
        cover_letter_snippet=content.get("cover_letter_snippet", ""),
        recommended_roles=strategy.get("recommended_roles", []),
        ats_keywords=strategy.get("ats_keywords", []),
        improvement_tips=strategy.get("improvement_tips", []),
    )
    extras = {
        "score_breakdown": gap.get("score_breakdown", {}),
        "seniority_match": gap.get("seniority_match", ""),
        "linkedin_headline": content.get("linkedin_headline", ""),
        "key_selling_points": content.get("key_selling_points", []),
        "quick_wins": strategy.get("quick_wins", []),
        "timeline": strategy.get("timeline", ""),
    }
    return result, extras

def answer_followup(question, analysis_context):
    user = f"=== ANALYSIS CONTEXT ===\n{json.dumps(analysis_context, indent=2)}\n\n=== USER QUESTION ===\n{question}"
    return call_llm(CHAT_SYSTEM_PROMPT, user, max_tokens=600)