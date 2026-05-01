from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from pydantic import BaseModel
from app.services.parser import extract_text, clean_text
from app.services.matcher import compute_match_score
from app.services.analyser import analyse, tailor_resume
import io

app = FastAPI(
    title="AI Resume Matcher",
    description="Match resumes to job descriptions using embeddings + Claude",
    version="1.0.0",
)

class MatchResult(BaseModel):
    match_score: float
    label: str
    present_skills: list[str]
    missing_skills: list[str]
    strengths: list[str]
    gaps: list[str]
    interview_tips: list[str]
    tailored_summary: str

@app.get("/health")
def health():
    return {"status": "ok", "version": "1.0.0"}

@app.post("/match", response_model=MatchResult)
async def match_resume(
    resume: UploadFile = File(..., description="Resume as PDF"),
    job_description: str = Form(..., description="Job description text")
):
    try:
        resume_bytes = await resume.read()
        resume_text = clean_text(extract_text(io.BytesIO(resume_bytes)))
    except Exception as e:
        raise HTTPException(400, f"Could not parse resume: {e}")

    if len(resume_text) < 50:
        raise HTTPException(400, "Resume text too short — check the PDF")

    score = compute_match_score(resume_text, job_description)
    analysis = analyse(resume_text, job_description)

    return MatchResult(
        match_score=score["match_score"],
        label=score["label"],
        **analysis
    )

@app.post("/tailor")
async def tailor(
    resume: UploadFile = File(...),
    job_description: str = Form(...)
):
    resume_bytes = await resume.read()
    resume_text = clean_text(extract_text(io.BytesIO(resume_bytes)))
    tailored = tailor_resume(resume_text, job_description)
    return {"tailored_resume": tailored}

@app.post("/match-text")
def match_text(resume_text: str = Form(...), job_description: str = Form(...)):
    score = compute_match_score(resume_text, job_description)
    analysis = analyse(resume_text, job_description)
    return {**score, **analysis}
