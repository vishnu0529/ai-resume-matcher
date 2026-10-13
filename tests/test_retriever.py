from app.services import retriever

FIXTURE_CORPUS = [
    {
        "skill": "Kubernetes",
        "aliases": ["k8s"],
        "category": "DevOps",
        "blurb": "Container orchestration platform for deploying and scaling containerised applications.",
        "resources": [{"title": "Kubernetes Official Documentation", "url": "https://kubernetes.io/docs/home/", "provider": "kubernetes.io"}],
    },
    {
        "skill": "Docker",
        "aliases": ["containerisation"],
        "category": "DevOps",
        "blurb": "Platform for packaging applications into portable containers.",
        "resources": [{"title": "Docker Official Get Started Guide", "url": "https://docs.docker.com/get-started/", "provider": "docker.com"}],
    },
    {
        "skill": "Python",
        "aliases": ["python3"],
        "category": "Languages",
        "blurb": "General-purpose programming language used for backend and data work.",
        "resources": [{"title": "Official Python Tutorial", "url": "https://docs.python.org/3/tutorial/", "provider": "python.org"}],
    },
]


def _fixture_collection():
    import chromadb

    client = chromadb.EphemeralClient()
    return retriever.build_collection(FIXTURE_CORPUS, client=client)


def test_load_corpus_parses_expected_shape():
    corpus = retriever.load_corpus()
    assert len(corpus) > 10
    entry = corpus[0]
    assert {"skill", "aliases", "category", "blurb", "resources"} <= entry.keys()
    assert isinstance(entry["resources"], list)
    assert "title" in entry["resources"][0]
    assert "url" in entry["resources"][0]


def test_search_resources_returns_matching_skill():
    collection = _fixture_collection()
    hits = retriever.search_resources("Kubernetes", collection=collection, k=2, min_similarity=0.0)
    assert len(hits) >= 1
    assert hits[0]["skill"] == "Kubernetes"
    assert hits[0]["url"] == "https://kubernetes.io/docs/home/"


def test_search_resources_filters_unrelated_skill_by_threshold():
    collection = _fixture_collection()
    hits = retriever.search_resources(
        "Interpretive Dance for Underwater Basket Weaving",
        collection=collection,
        k=2,
        min_similarity=0.9,
    )
    assert hits == []
