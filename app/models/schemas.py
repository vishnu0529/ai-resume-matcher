from pydantic import BaseModel, Field
from typing import Optional

class SkillGap(BaseModel):
    skill: str
    importance: str
    how_to_acquire: str

class MatchResponse(BaseModel):
    match_score: int = Field(..., ge=0, le=100)
    grade: str
    matched_skills: list[str]
    missing_skills: list[SkillGap]
    strengths: list[str]
    weaknesses: list[str]
    tailored_summary: str
    cover_letter_snippet: str
    recommended_roles: list[str]
    ats_keywords: list[str]
    improvement_tips: list[str]

class HealthResponse(BaseModel):
    status: str
    version: str
    llm_provider: str
