import streamlit as st
import requests

st.title("AI Resume Matcher")

resume_file = st.file_uploader("Upload your resume", type=["pdf", "txt"])
job_description = st.text_area("Job description")

if st.button("Evaluate") and resume_file and job_description:
    files = {"resume": (resume_file.name, resume_file.getvalue())}
    data = {"job_description": job_description}
    response = requests.post("http://localhost:8000/api/v1/match", files=files, data=data)
    if response.ok:
        st.json(response.json())
    else:
        st.error(f"Request failed: {response.status_code}")
