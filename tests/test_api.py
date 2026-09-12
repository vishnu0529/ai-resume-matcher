from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.models.schemas import MatchResponse
from app.services.matcher import score_grade
from app.services.parser import clean_text, extract_text_from_file, truncate

client = TestClient(app)

SAMPLE_RESUME_TEXT = (
    "Vishnu — AI Engineer. " + "Python, FastAPI, LangGraph, RAG pipelines, Docker. " * 5
)
SAMPLE_JD_TEXT = "We are hiring an AI Engineer with Python, FastAPI, and LLM orchestration experience."

FAKE_MATCH_RESULT = MatchResponse(
    match_score=72,
    grade="B",
    matched_skills=["Python", "FastAPI"],
    missing_skills=[],
    strengths=["Strong LLM fundamentals"],
    weaknesses=["No cloud deployment experience"],
    tailored_summary="AI Engineer with hands-on LLM experience.",
    cover_letter_snippet="My experience building RAG pipelines...",
    recommended_roles=["AI Engineer"],
    ats_keywords=["LLM", "Python"],
    improvement_tips=["Add Docker to your skills section"],
)
FAKE_EXTRAS = {
    "score_breakdown": {"technical_skills": 30, "experience_level": 20, "domain_fit": 15, "soft_skills": 7},
    "seniority_match": "match",
    "linkedin_headline": "AI Engineer | Python & LLMs",
    "key_selling_points": ["Built production RAG pipelines"],
    "quick_wins": ["Add Docker to your resume"],
    "timeline": "2-4 weeks",
}


def test_health():
    resp = client.get("/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ok"
    assert "llm_provider" in data


def test_match_rejects_missing_resume_and_text():
    resp = client.post("/api/v1/match", data={"job_description": SAMPLE_JD_TEXT})
    assert resp.status_code == 400
    assert "resume" in resp.json()["detail"].lower()


def test_match_rejects_short_resume_text():
    resp = client.post(
        "/api/v1/match", data={"job_description": SAMPLE_JD_TEXT, "resume_text": "too short"}
    )
    assert resp.status_code == 400
    assert "resume" in resp.json()["detail"].lower()


def test_match_rejects_short_job_description():
    resp = client.post(
        "/api/v1/match", data={"job_description": "too short", "resume_text": SAMPLE_RESUME_TEXT}
    )
    assert resp.status_code == 400
    assert "job description" in resp.json()["detail"].lower()


def test_match_with_agent_pipeline_returns_combined_response():
    with patch(
        "app.services.recruiter_agent.run_agent", return_value=(FAKE_MATCH_RESULT, FAKE_EXTRAS)
    ) as mock_run:
        resp = client.post(
            "/api/v1/match",
            data={
                "job_description": SAMPLE_JD_TEXT,
                "resume_text": SAMPLE_RESUME_TEXT,
                "use_agent": "true",
            },
        )

    assert resp.status_code == 200
    data = resp.json()
    assert data["match_score"] == 72
    assert data["grade"] == "B"
    assert data["linkedin_headline"] == "AI Engineer | Python & LLMs"
    assert data["quick_wins"] == ["Add Docker to your resume"]
    mock_run.assert_called_once()


def test_match_without_agent_uses_single_shot_matcher():
    with patch("app.services.matcher.analyse", return_value=FAKE_MATCH_RESULT) as mock_analyse:
        resp = client.post(
            "/api/v1/match",
            data={
                "job_description": SAMPLE_JD_TEXT,
                "resume_text": SAMPLE_RESUME_TEXT,
                "use_agent": "false",
            },
        )

    assert resp.status_code == 200
    assert resp.json()["match_score"] == 72
    mock_analyse.assert_called_once()


def test_match_returns_500_on_llm_json_error():
    with patch("app.services.recruiter_agent.run_agent", side_effect=ValueError("bad json")):
        resp = client.post(
            "/api/v1/match",
            data={"job_description": SAMPLE_JD_TEXT, "resume_text": SAMPLE_RESUME_TEXT},
        )

    assert resp.status_code == 500
    assert "LLM analysis failed" in resp.json()["detail"]


def test_chat_followup_returns_answer():
    with patch(
        "app.services.recruiter_agent.answer_followup", return_value="Focus on Docker next."
    ) as mock_chat:
        resp = client.post(
            "/api/v1/chat",
            json={"question": "What should I learn first?", "analysis_context": {"match_score": 72}},
        )

    assert resp.status_code == 200
    assert resp.json()["answer"] == "Focus on Docker next."
    mock_chat.assert_called_once()


def test_chat_followup_returns_500_on_error():
    with patch("app.services.recruiter_agent.answer_followup", side_effect=RuntimeError("boom")):
        resp = client.post(
            "/api/v1/chat", json={"question": "Why?", "analysis_context": {}}
        )

    assert resp.status_code == 500


@pytest.mark.parametrize(
    "score,expected_grade",
    [(90, "A"), (85, "A"), (75, "B"), (70, "B"), (60, "C"), (55, "C"), (45, "D"), (40, "D"), (10, "F")],
)
def test_score_grade_boundaries(score, expected_grade):
    assert score_grade(score) == expected_grade


def test_clean_text_collapses_whitespace_and_blank_lines():
    messy = "Line one   with  spaces \n\n\n\nLine two\t\there"
    cleaned = clean_text(messy)
    assert "   " not in cleaned
    assert "\n\n\n" not in cleaned


def test_truncate_leaves_short_text_untouched():
    text = "short text"
    assert truncate(text, max_chars=100) == text


def test_truncate_cuts_long_text_with_marker():
    text = "a" * 200
    result = truncate(text, max_chars=50)
    assert len(result) < len(text)
    assert result.endswith("[... truncated ...]")


def test_extract_text_from_file_handles_txt():
    content = extract_text_from_file("resume.txt", b"Plain text resume content")
    assert content == "Plain text resume content"


def test_extract_text_from_file_rejects_unsupported_extension():
    with pytest.raises(ValueError, match="Unsupported file type"):
        extract_text_from_file("resume.docx", b"whatever")
