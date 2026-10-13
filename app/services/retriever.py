import json
import logging
from pathlib import Path
from typing import Any, Optional

from app.core.config import settings

logger = logging.getLogger(__name__)

CORPUS_PATH = Path(__file__).resolve().parent.parent.parent / "data" / "knowledge_base" / "skill_resources.json"
COLLECTION_NAME = "skill_resources"

_collection = None


def load_corpus(path: Path = CORPUS_PATH) -> list[dict[str, Any]]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _embedding_text(entry: dict[str, Any]) -> str:
    aliases = " ".join(entry.get("aliases", []))
    return f"{entry['skill']}. {aliases}. {entry.get('blurb', '')}".strip()


def build_collection(corpus: list[dict[str, Any]], client=None):
    import chromadb

    client = client or chromadb.EphemeralClient()
    collection = client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},
    )
    collection.upsert(
        ids=[entry["skill"] for entry in corpus],
        documents=[_embedding_text(entry) for entry in corpus],
        metadatas=[
            {
                "skill": entry["skill"],
                "resources_json": json.dumps(entry.get("resources", [])),
            }
            for entry in corpus
        ],
    )
    return collection


def ensure_index() -> None:
    """Eagerly build and cache the default collection so the first real
    request doesn't pay the embedding cost. Safe to call multiple times."""
    global _collection
    if _collection is not None:
        return
    try:
        corpus = load_corpus()
        _collection = build_collection(corpus)
        logger.info("RAG index built: %d skill resources indexed.", len(corpus))
    except Exception:
        logger.exception("Failed to build RAG index — skill-gap advice will be ungrounded.")
        _collection = None


def search_resources(
    skill_name: str,
    collection=None,
    k: Optional[int] = None,
    min_similarity: Optional[float] = None,
) -> list[dict[str, Any]]:
    k = k if k is not None else settings.RAG_TOP_K
    min_similarity = min_similarity if min_similarity is not None else settings.RAG_MIN_SIMILARITY

    target = collection
    if target is None:
        ensure_index()
        target = _collection
    if target is None:
        return []

    try:
        result = target.query(query_texts=[skill_name], n_results=k)
    except Exception:
        logger.exception("RAG retrieval failed for skill %r.", skill_name)
        return []

    distances = result.get("distances", [[]])[0]
    metadatas = result.get("metadatas", [[]])[0]

    hits = []
    for distance, metadata in zip(distances, metadatas):
        similarity = 1 - distance
        if similarity < min_similarity:
            continue
        resources = json.loads(metadata.get("resources_json", "[]"))
        for resource in resources:
            hits.append({**resource, "skill": metadata.get("skill", skill_name), "similarity": round(similarity, 3)})
    return hits
