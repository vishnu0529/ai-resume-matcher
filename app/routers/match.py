import logging
from typing import Optional
from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from pydantic import BaseModel
from app.core.config import settings
from app.models.schemas import MatchResponse
from app.services.parser import parse_jd, parse_resume

logger = logging.getLogger(__name__)
router = APIRouter()
MAX_BYTES = settings.MAX_RESUME_SIZE_MB * 1024 * 1024


class AgentMatchResponse(MatchResponse):
    score_breakdown: dict = {}
    seniority_match: str = ""
    linkedin_headline: str = ""
    key_selling_points: list[str] = []
    quick_wins: list[str] = []
    timeline: str = ""


class ChatRequest(BaseModel):
    question: str
    analysis_context: dict


class ChatResponse(BaseModel):
    answer: str


async def _parse_resume_input(resume, resume_text):
    if resume is not None:
        content = await resume.read()
        if len(content) > MAX_BYTES:
            raise HTTPException(status_code=400, detail=f"Resume exceeds {settings.MAX_RESUME_SIZE_MB} MB limit.")
        try:
            return parse_resume(resume.filename or "resume.pdf", content)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc))
    elif resume_text:
        return resume_text.strip()
    else:
        raise HTTPException(status_code=400, detail="Provide either a resume file or resume_text.")


@router.post("/match", response_model=AgentMatchResponse)
async def match_resume(
    job_description: str = Form(...),
    resume: Optional[UploadFile] = File(None),
    resume_text: Optional[str] = Form(None),
    use_agent: str = Form("true"),
):
    parsed_resume = await _parse_resume_input(resume, resume_text)
    if len(parsed_resume) < 100:
        raise HTTPException(status_code=400, detail="Resume text is too short.")
    parsed_jd = parse_jd(job_description)
    if len(parsed_jd) < 50:
        raise HTTPException(status_code=400, detail="Job description is too short.")
    try:
        if use_agent.lower() == "true":
            from app.services.recruiter_agent import run_agent
            result, extras = run_agent(parsed_resume, parsed_jd)
            return AgentMatchResponse(**result.model_dump(), **extras)
        else:
            from app.services.matcher import analyse
            result = analyse(parsed_resume, parsed_jd)
            return AgentMatchResponse(**result.model_dump())
    except ValueError as exc:
        raise HTTPException(status_code=500, detail=f"LLM analysis failed: {exc}")
    except Exception:
        logger.exception("Unexpected error during analysis")
        raise HTTPException(status_code=500, detail="Internal analysis error.")


@router.post("/chat", response_model=ChatResponse)
async def chat_followup(request: ChatRequest):
    try:
        from app.services.recruiter_agent import answer_followup
        answer = answer_followup(request.question, request.analysis_context)
        return ChatResponse(answer=answer)
    except Exception:
        logger.exception("Chat error")
        raise HTTPException(status_code=500, detail="Chat error.")