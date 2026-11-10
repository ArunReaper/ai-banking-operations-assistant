from pathlib import Path

import pytest
from backend.rag import vector_store


def fake_embeddings(texts: list[str]) -> list[list[float]]:
    """Return deterministic embeddings for isolated unit tests."""
    return [[1.0] + [0.0] * 383 for _ in texts]


@pytest.fixture
def collection(tmp_path: Path):
    return vector_store.get_chroma_collection(tmp_path / "chroma")


def test_create_chroma_collection(collection):
    assert collection.name == vector_store.COLLECTION_NAME
    assert collection.count() == 0


def test_add_document_chunks(monkeypatch, collection):
    monkeypatch.setattr(
        vector_store,
        "generate_embeddings",
        fake_embeddings,
    )

    chunks = [
        {
            "id": "chunk-001",
            "content": "IMPS gateway timeout investigation.",
            "metadata": {
                "document_id": "SOP-IMPS-001",
                "chunk_index": 0,
            },
        }
    ]

    inserted = vector_store.add_document_chunks(collection, chunks)

    assert inserted == 1
    assert collection.count() == 1


def test_upsert_does_not_create_duplicates(monkeypatch, collection):
    monkeypatch.setattr(
        vector_store,
        "generate_embeddings",
        fake_embeddings,
    )

    chunks = [
        {
            "id": "chunk-001",
            "content": "IMPS gateway timeout investigation.",
            "metadata": {"document_id": "SOP-IMPS-001"},
        }
    ]

    vector_store.add_document_chunks(collection, chunks)
    vector_store.add_document_chunks(collection, chunks)

    assert collection.count() == 1


def test_add_empty_chunks(collection):
    assert vector_store.add_document_chunks(collection, []) == 0
    assert collection.count() == 0


def test_search_similar_chunks(monkeypatch, collection):
    monkeypatch.setattr(
        vector_store,
        "generate_embeddings",
        fake_embeddings,
    )

    chunks = [
        {
            "id": "chunk-001",
            "content": "IMPS gateway timeout investigation.",
            "metadata": {"document_id": "SOP-IMPS-001"},
        },
        {
            "id": "chunk-002",
            "content": "Insufficient funds investigation.",
            "metadata": {"document_id": "SOP-BAL-001"},
        },
    ]

    vector_store.add_document_chunks(collection, chunks)

    results = vector_store.search_similar_chunks(
        collection,
        "Why did the IMPS payment time out?",
        n_results=2,
    )

    assert len(results) == 2
    assert results[0]["content"] in [
        chunk["content"] for chunk in chunks
    ]
    assert "distance" in results[0]
    assert "metadata" in results[0]


def test_search_empty_collection(collection):
    results = vector_store.search_similar_chunks(
        collection,
        "IMPS transaction failure",
    )

    assert results == []


def test_search_rejects_empty_query(collection):
    with pytest.raises(ValueError):
        vector_store.search_similar_chunks(collection, "  ")


def test_search_rejects_invalid_result_count(collection):
    with pytest.raises(ValueError):
        vector_store.search_similar_chunks(
            collection,
            "IMPS failure",
            n_results=0,
        )