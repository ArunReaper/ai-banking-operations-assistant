import pytest
from backend.rag.chunker import (
    create_document_chunks,
    split_into_chunks,
)


def test_short_text_returns_single_chunk():
    text = "This is a short document."

    chunks = split_into_chunks(
        text,
        chunk_size=100,
        chunk_overlap=20,
    )
    assert chunks == [text]


def test_empty_text_returns_no_chunks():
    assert split_into_chunks("   ") == []


def test_long_text_is_split():
    text = "A" * 2500

    chunks = split_into_chunks(
        text,
        chunk_size=1000,
        chunk_overlap=150,
    )

    assert len(chunks) >= 3
    assert all(len(chunk) <= 1000 for chunk in chunks)


def test_chunks_preserve_content():
    text = "A" * 2500

    chunks = split_into_chunks(
        text,
        chunk_size=1000,
        chunk_overlap=150,
    )

    reconstructed = "".join(chunks)

    assert len(reconstructed) > len(text)


def test_invalid_chunk_size_raises_error():
    with pytest.raises(ValueError):
        split_into_chunks("Sample text", chunk_size=0)


def test_invalid_overlap_raises_error():
    with pytest.raises(ValueError):
        split_into_chunks(
            "Sample text",
            chunk_size=100,
            chunk_overlap=100,
        )


def test_create_document_chunks_preserves_metadata():
    documents = [
        {
            "content": "A" * 1500,
            "metadata": {
                "document_id": "SOP-001",
                "source": "sample.md",
                "title": "Sample SOP",
            },
        }
    ]

    chunks = create_document_chunks(documents, chunk_size=1000, chunk_overlap=150)

    assert len(chunks) >= 2
    assert chunks[0]["metadata"]["document_id"] == "SOP-001"
    assert chunks[0]["metadata"]["source"] == "sample.md"
    assert chunks[0]["metadata"]["chunk_index"] == 0
    assert len(chunks[0]["id"]) == 64


def test_chunk_ids_are_deterministic():
    documents = [
        {
            "content": "Sample document content.",
            "metadata": {
                "document_id": "SOP-001",
                "source": "sample.md",
            },
        }
    ]

    first = create_document_chunks(documents)
    second = create_document_chunks(documents)

    assert first[0]["id"] == second[0]["id"]