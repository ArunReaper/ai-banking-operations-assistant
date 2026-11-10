from backend.rag.embedding_service import generate_embeddings


def test_generate_embeddings():
    texts = [
        "The IMPS transaction failed because of a gateway timeout.",
        "The account has insufficient funds.",
    ]

    embeddings = generate_embeddings(texts)

    assert len(embeddings) == 2
    assert len(embeddings[0]) == 384
    assert len(embeddings[1]) == 384


def test_generate_embeddings_returns_empty_list():
    assert generate_embeddings([]) == []
