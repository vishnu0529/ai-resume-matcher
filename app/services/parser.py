import pdfplumber
from pathlib import Path


def extract_text(source) -> str:
    """Accept a file path string, Path, or file-like object."""
    if isinstance(source, (str, Path)):
        with pdfplumber.open(source) as pdf:
            return "\n".join(p.extract_text() or "" for p in pdf.pages)
    else:
        with pdfplumber.open(source) as pdf:
            return "\n".join(p.extract_text() or "" for p in pdf.pages)


def clean_text(text: str) -> str:
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    return "\n".join(lines)
