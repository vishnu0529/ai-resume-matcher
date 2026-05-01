from app.services.matcher import compute_match_score
from app.services.analyser import analyse

resume = """
John Smith | Python Developer
Skills: Python, FastAPI, SQL, Git, REST APIs
Experience: 2 years backend development at Acme Corp
Built REST APIs serving 10k daily users
"""

job = """
We're hiring an AI Engineer. Requirements:
Python, FastAPI, LLMs, vector databases, RAG pipelines, API design.
Experience with Anthropic or OpenAI APIs preferred.
"""

score = compute_match_score(resume, job)
print("Match score:", score)

analysis = analyse(resume, job)
print("Present skills:", analysis["present_skills"])
print("Missing skills:", analysis["missing_skills"])
print("Summary:", analysis["tailored_summary"])
