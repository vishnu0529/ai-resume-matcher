from dotenv import load_dotenv
load_dotenv()

from app.services.matcher import compute_match_score
from app.services.analyser import analyse

resume = """
Vishnu — Python Developer
Skills: Python, FastAPI, REST APIs, SQL, Git, Pandas, NumPy, NLP
Experience: 2 years backend development
Built REST APIs, NLP sentiment pipeline, deployed on Railway.
"""

job = """
AI Engineer — Python, FastAPI, LLMs, RAG, vector databases.
Build production AI systems with Claude or OpenAI.
NLP experience a plus.
"""

print("Step 1: Computing match score...")
score = compute_match_score(resume, job)
print(f"  Score: {score['match_score']}%  ({score['label']})")

print("Step 2: Running LLM analysis...")
analysis = analyse(resume, job)
print(f"  Present: {analysis['present_skills']}")
print(f"  Missing: {analysis['missing_skills']}")

print("Step 3: Building combined result...")
full_result = {
    "match_score": score["match_score"],
    "label": score["label"],
    **analysis
}

required_keys = [
    "match_score", "label", "present_skills", "missing_skills",
    "strengths", "gaps", "interview_tips", "tailored_summary"
]
for key in required_keys:
    assert key in full_result, f"Missing key: {key}"

print(f"\nFull result keys: {list(full_result.keys())}")
print(f"Match: {full_result['match_score']}% — {full_result['label']}")
print(f"Present: {len(full_result['present_skills'])} skills")
print(f"Missing: {len(full_result['missing_skills'])} skills")
print("\nFull pipeline test passed! Ready to build the API.")
