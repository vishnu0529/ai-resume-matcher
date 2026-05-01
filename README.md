# AI Resume Matcher

Mini AI recruiter prototype for resume and job description matching.

## Structure

- `app/main.py` - FastAPI application entrypoint
- `app/services/parser.py` - resume / JD parsing utilities
- `app/services/matcher.py` - matching logic and score output
- `app/services/analyser.py` - skills analysis and recommendations
- `dashboard.py` - Streamlit dashboard prototype

## Install

```bash
python -m pip install -r requirements.txt
```

## Run

```bash
uvicorn app.main:app --reload
```

```bash
streamlit run dashboard.py
```
