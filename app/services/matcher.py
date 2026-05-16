import logging
from app.services.llm_client import call_llm_json
from app.models.schemas import MatchResponse, SkillGap

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """
You are an expert AI recruitment analyst. Evaluate the candidate's resume against the job description and return a structured, honest assessment.

Rules:
- Be specific. Reference actual skills and technologies from the texts.
- Match score must reflect real alignment, not optimism.
- ATS keywords must be exact strings from the job description.
- Return ONLY valid JSON matching the schema below. No markdown, no extra prose.

JSON schema:
{
  "match_score": <int 0-100>,
  "grade": <"A"|"B"|"C"|"D"|"F">,
  "matched_skills": [<string>],
  "missing_skills": [
    {
      "skill": <string>,
      "importance": <"critical"|"nice-to-have">,
      "how_to_acquire": <string>
    }
  ],
  "strengths": [<string>],
  "weaknesses": [<string>],
  "tailored_summary": <string>,
  "cover_letter_snippet": <string>,
  "recommended_roles": [<string>],
  "ats_keywords": [<string>],
  "improvement_tips": [<string>]
}
""".strip()

def score_grade(score: int) -> str:
    if score >= 85: return "A"
    if score >= 70: return "B"
    if score >= 55: return "C"
    if score >= 40: return "D"
    return "F"

def analyse(resume_text: str, job_description: str) -> MatchResponse:
    user_prompt = f"=== RESUME ===\n{resume_text}\n\n=== JOB DESCRIPTION ===\n{job_description}\n\nAnalyse and return the JSON assessment."
    logger.info("Sending to LLM for analysis...")
    data = call_llm_json(SYSTEM_PROMPT, user_prompt, max_tokens=2500)
    score = int(data.get("match_score", 0))
    missing_skills = [
        SkillGap(
            skill=g.get("skill", ""),
            importance=g.get("importance", "nice-to-have"),
            how_to_acquire=g.get("how_to_acquire", ""),
        )
        for g in data.get("missing_skills", [])
    ]
    return MatchResponse(
        match_score=score,
        grade=data.get("grade") or score_grade(score),
        matched_skills=data.get("matched_skills", []),
        missing_skills=missing_skills,
        strengths=data.get("strengths", []),
        weaknesses=data.get("weaknesses", []),
        tailored_summary=data.get("tailored_summary", ""),
        cover_letter_snippet=data.get("cover_letter_snippet", ""),
        recommended_roles=data.get("recommended_roles", []),
        ats_keywords=data.get("ats_keywords", []),
        improvement_tips=data.get("improvement_tips", []),
    )
