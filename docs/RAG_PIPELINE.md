# RAG Pipeline — Grounded Skill-Gap Advice

## Why

Before this change, the `how_to_acquire` advice for each skill gap (and the
improvement tips built on top of it) came purely from the LLM's own
training knowledge — no citation, no way to verify it, and no guarantee the
suggested course or doc still exists. This adds a small retrieval step so
that advice is grounded in a curated set of real resources wherever one is
available, and falls back honestly (no fabricated source) when it isn't.

## How it works

```
Step 2: Gap Analyser          → missing_skills: [{skill, importance}]
                 |
Retrieval (pure Python, no LLM call)
  app/services/retriever.py  → search_resources(skill) per missing skill
                 |
Step 4: Strategist (existing LLM call, extended)
  receives RETRIEVED_RESOURCES alongside its usual inputs
  → writes how_to_acquire PER SKILL, citing only what was retrieved
                 |
run_agent() merges the Strategist's {text, source_title, source_url}
  back onto each SkillGap, and builds a flat `rag_sources` list for the API response
```

No extra LLM round-trip is added — retrieval happens in Python between the
existing Step 2 and Step 4 calls, and the result is folded into Step 4's
existing prompt. Cost and latency only grow by the retrieval query itself
(a few milliseconds, in-memory).

## Corpus

`data/knowledge_base/skill_resources.json` — ~60 hand-curated entries:

```json
{
  "skill": "Kubernetes",
  "aliases": ["k8s"],
  "category": "DevOps",
  "blurb": "Container orchestration platform for deploying, scaling, and managing containerised applications.",
  "resources": [
    {"title": "Kubernetes Official Documentation", "url": "https://kubernetes.io/docs/home/", "provider": "kubernetes.io"}
  ]
}
```

**To add a skill**: just append an entry to the JSON file. There's no
separate index-build step — the index is rebuilt in memory from this file
every time the process starts (see "Embeddings and index" below), so a new
entry is live on the next restart/deploy.

**Known limitation**: these resource links were authored from training
knowledge, not verified by live browsing. They point at stable, well-known
homepages (official docs, freeCodeCamp, MDN, Coursera) on purpose, to
minimise link rot, but should be spot-checked periodically.

## Embeddings and index

- **Embedding model**: Chroma's bundled default embedding function (an
  ONNX MiniLM model). No API key, no torch dependency, and it works even
  if neither `GOOGLE_API_KEY` nor `ANTHROPIC_API_KEY` is set — retrieval is
  fully decoupled from `LLM_PROVIDER`.
- **Vector store**: Chroma, in-memory/ephemeral (`chromadb.EphemeralClient()`).
  Rebuilt from the JSON corpus at FastAPI startup (`app/main.py` lifespan
  calls `retriever.ensure_index()`), and lazily on first use otherwise.
  No persisted index file — nothing to go stale, nothing that needs a
  rebuild step, and it survives Render's ephemeral filesystem across
  redeploys with zero extra ops work. Embedding ~60 short entries takes
  about 1-2 seconds.
- **Similarity space**: the collection is created with
  `metadata={"hnsw:space": "cosine"}` explicitly, so `similarity = 1 - distance`
  is the correct conversion from Chroma's returned distance.

## Retrieval tuning

- `RAG_TOP_K` (default `2`) and `RAG_MIN_SIMILARITY` (default `0.35`) in
  `app/core/config.py`.
- Measured against the production corpus: an exact skill match scores
  ~0.7 similarity; a genuinely unrelated skill (e.g. "Quantum
  Chromodynamics") scores ~0.1 and is correctly filtered out below the
  threshold. Closely related skills (e.g. Docker/Kubernetes) sometimes
  both clear the threshold for each other's query — this is expected and
  mostly harmless (the Strategist still picks the resource that matches
  the skill it's writing about), not a bug to chase.

## Graceful degradation

Any failure in `app/services/retriever.py` (corpus missing, chromadb
import error, embedding failure, etc.) is caught and logged; the function
returns `[]` instead of raising. The pipeline then produces ungrounded
advice with empty `source_title`/`source_url` rather than a 500. This was
verified by temporarily removing the corpus file and confirming
`search_resources()` returns `[]` cleanly (no crash).

## Scope / what's not covered (v1)

- Only the agentic pipeline (`recruiter_agent.py`, `use_agent=true`) is
  grounded. The single-shot fallback path (`matcher.py`, `use_agent=false`)
  is unchanged — lower priority, documented as future work below.
- The corpus is a static, hand-curated snapshot — not a live web search or
  job-market API.

## Roadmap

- Extend grounding to the single-shot `matcher.py` path.
- Add a second corpus of strong resume-bullet / cover-letter examples to
  ground `tailored_summary` and `cover_letter_snippet` the same way skill
  advice is grounded now.
- Swap the static corpus for a live source (e.g. a jobs-market API) if
  resource freshness becomes a real requirement.
