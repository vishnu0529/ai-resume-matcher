from dotenv import load_dotenv
load_dotenv()

from app.services.analyser import analyse, tailor_resume

resume = """
Vishnu — Python Developer
Skills: Python, FastAPI, REST APIs, SQL, Git, Pandas, NumPy
Experience: 2 years backend development
- Built REST APIs serving 10k daily users
- NLP sentiment analysis pipeline (BERT-based)
- Deployed services on Railway and Render
"""

job = """
AI Engineer — London (Remote friendly)
Requirements:
- Python, FastAPI (required)
- LLM integration: Anthropic Claude or OpenAI (required)
- RAG pipelines and vector databases (FAISS, Pinecone, Chroma)
- Experience deploying ML models to production
- NLP / transformers experience a plus
"""

print("Calling Claude for analysis (takes ~5s)...")
result = analyse(resume, job)

print("\n--- Skills analysis ---")
print("Present skills:", result["present_skills"])
print("Missing skills:", result["missing_skills"])
print("Strengths:", result["strengths"])
print("Gaps:", result["gaps"])
print("Interview tips:", result["interview_tips"])
print("\nTailored summary:")
print(result["tailored_summary"])

assert isinstance(result["present_skills"], list), "present_skills must be a list"
assert isinstance(result["missing_skills"], list), "missing_skills must be a list"
assert len(result["tailored_summary"]) > 50, "tailored_summary too short"
print("\nAll analyser tests passed!")

print("\n--- Testing resume tailoring (takes ~8s) ---")
tailored = tailor_resume(resume, job)
print(tailored[:400], "...")
assert len(tailored) > 100, "Tailored resume too short"
print("\nTailor test passed!")
