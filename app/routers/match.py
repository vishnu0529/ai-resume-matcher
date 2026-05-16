import logging
from typing import Optional
from fastapi import APIRouter, File, Form, HTTPException, UploadFile, status
from app.core.config import settings
from app.models.schemas import MatchResponse
from app.services.matcher import analyse
from app.services.parser import parse_jd, parse_resume

logger = logging.getLogger(__name__)
router = APIRouter()
MAX_BYTES = settings.MAX_RESUME_SIZE_MB * 1024 * 1024

@router.post("/match", response_model=MatchResponse)
async def match_resume(
    job_description: str = Form(...),
    resume: Optional[UploadFile] = File(None),
    resume_text: Optional[str] = Form(None),
):
    if resume is not None:
        content = await resume.read()
        if len(content) > MAX_BYTES:
            raise HTTPException(status_code=400, detail=f"Resume exceeds {settings.MAX_RESUME_SIZE_MB} MB limit.")
        try:
            parsed_resume = parse_resume(resume.filename or "resume.pdf", content)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc))
    elif resume_text:
        parsed_resume = resume_text.strip()
    else:
        raise HTTPException(status_code=400, detail="Provide either a resume file or resume_text.")

    if len(parsed_resume) < 100:
        raise HTTPException(status_code=400, detail="Resume text is too short to analyse.")

    parsed_jd = parse_jd(job_description)
    if len(parsed_jd) < 50:
        raise HTTPException(status_code=400, detail="Job description is too short.")

    try:
        return analyse(parsed_resume, parsed_jd)
    except ValueError as exc:
        raise HTTPException(status_code=500, detail=f"LLM analysis failed: {exc}")
    except Exception:
        logger.exception("Unexpected error during analysis")
        raise HTTPException(status_code=500, detail="Internal analysis error.")
