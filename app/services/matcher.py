import re
import numpy as np
from typing import Dict, Optional

_model = None
_faiss = None


def get_model() -> Optional[object]:
    global _model
    if _model is None:
        try:
            from sentence_transformers import SentenceTransformer
            _model = SentenceTransformer("all-MiniLM-L6-v2")
        except Exception:
            _model = None
    return _model


def get_faiss() -> Optional[object]:
    global _faiss
    if _faiss is None:
        try:
            import faiss
            _faiss = faiss
        except Exception:
            _faiss = None
    return _faiss


def compute_match_score(resume_text: str, job_text: str) -> dict:
    model = get_model()
    faiss_lib = get_faiss()
    if model is None or faiss_lib is None:
        return _fallback_match_score(resume_text, job_text)

    resume_chunks = _chunk(resume_text)
    job_chunks = _chunk(job_text)

    try:
        resume_embs = model.encode(resume_chunks, normalize_embeddings=True)
        job_embs = model.encode(job_chunks, normalize_embeddings=True)
    except Exception:
        return _fallback_match_score(resume_text, job_text)

    resume_matrix = np.array(resume_embs, dtype="float32")
    job_matrix = np.array(job_embs, dtype="float32")

    dim = resume_matrix.shape[1]
    index = faiss_lib.IndexFlatIP(dim)
    index.add(resume_matrix)

    scores = []
    for je in job_matrix:
        D, _ = index.search(np.expand_dims(je, axis=0), k=1)
        scores.append(float(D[0][0]))

    avg_score = float(np.mean(scores)) if scores else 0.0
    pct = round(min(avg_score * 100, 100), 1)

    return {
        "match_score": pct,
        "label": _label(pct),
        "chunks_compared": len(job_chunks),
    }


def _fallback_match_score(resume_text: str, job_text: str) -> dict:
    resume_tokens = set(re.findall(r"\w+", resume_text.lower()))
    job_tokens = set(re.findall(r"\w+", job_text.lower()))
    overlap = resume_tokens.intersection(job_tokens)
    pct = round(len(overlap) / max(1, len(job_tokens)) * 100, 1)
    return {
        "match_score": pct,
        "label": _label(pct),
        "chunks_compared": 1,
        "fallback": True,
    }


def _chunk(text: str, size: int = 100) -> list[str]:
    words = text.split()
    chunks = [" ".join(words[i:i+size]) for i in range(0, len(words), size)]
    return chunks or [text]


def _label(score: float) -> str:
    if score >= 80:
        return "Excellent match"
    if score >= 60:
        return "Good match"
    if score >= 40:
        return "Partial match"
    return "Low match"
