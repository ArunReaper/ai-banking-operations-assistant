
from unittest.mock import patch

import pytest
from backend.rag.retrieval_service import retrieve_relevant_documents


@patch("backend.rag.retrieval_service.search_similar_chunks")
@patch("backend.rag.retrieval_service.get_chroma_collection")
def test_retrieve_relevant_documents(
        mock_get_collection,
        mock_search,
):
    mock_get_collection.return_value = "mock_collection"

    mock_search.return_value = [
        {
            "content": "A pending transaction must not be communicated as refunded.",
            "metadata": {
                "source": "imps_failure_handling.md",
                "title": "Synthetic SOP: IMPS Transaction Failure Handling",
                "document_id": "SOP-IMPS-001",
                "version": "1.0",
            },
            "distance": 0.25,
        }
    ]

    results = retrieve_relevant_documents(
        "Can we confirm a refund when a transaction is pending?"
    )

    assert len(results) == 1
    assert results[0]["document_id"] == "SOP-IMPS-001"
    assert results[0]["distance"] == 0.25
    assert "must not be communicated as refunded" in results[0]["content"]

    mock_search.assert_called_once()


def test_empty_query_raises_error():
    with pytest.raises(ValueError, match="Query cannot be empty"):
        retrieve_relevant_documents("  ")


def test_invalid_result_count_raises_error():
    with pytest.raises(ValueError, match="Number of results must be positive"):
        retrieve_relevant_documents("IMPS payment failure", n_results=0)


def test_retrieve_relevant_documents_filters_weak_matches(monkeypatch):
    """Results above the cosine-distance threshold are discarded."""

    from unittest.mock import MagicMock

    from backend.rag import retrieval_service

    monkeypatch.setattr(
        retrieval_service,
        "get_chroma_collection",
        MagicMock(),
    )

    monkeypatch.setattr(
        retrieval_service,
        "search_similar_chunks",
        lambda **kwargs: [
            {
                "content": "Relevant SOP content",
                "metadata": {
                    "source": "upi_failure_handling.md",
                    "title": "UPI Failure Handling",
                    "document_id": "SOP-UPI-001",
                    "version": "1.0",
                },
                "distance": 0.40,
            },
            {
                "content": "Irrelevant SOP content",
                "metadata": {
                    "source": "imps_failure_handling.md",
                    "title": "IMPS Failure Handling",
                    "document_id": "SOP-IMPS-001",
                    "version": "1.0",
                },
                "distance": 0.90,
            },
        ],
    )

    results = retrieval_service.retrieve_relevant_documents(
        query="Why did my UPI payment fail?"
    )

    assert len(results) == 1
    assert results[0]["document_id"] == "SOP-UPI-001"


def test_retrieve_relevant_documents_returns_empty_for_weak_matches(
        monkeypatch,
):
    """No documents are returned when all results are weak matches."""

    from unittest.mock import MagicMock

    from backend.rag import retrieval_service

    monkeypatch.setattr(
        retrieval_service,
        "get_chroma_collection",
        MagicMock(),
    )

    monkeypatch.setattr(
        retrieval_service,
        "search_similar_chunks",
        lambda **kwargs: [
            {
                "content": "Unrelated content",
                "metadata": {
                    "source": "upi_failure_handling.md",
                    "title": "UPI Failure Handling",
                    "document_id": "SOP-UPI-001",
                    "version": "1.0",
                },
                "distance": 0.95,
            },
        ],
    )

    results = retrieval_service.retrieve_relevant_documents(
        query="What is the weather in Mumbai?"
    )

    assert results == []


def test_retrieve_relevant_documents_rejects_invalid_threshold():
    from backend.rag.retrieval_service import retrieve_relevant_documents

    with pytest.raises(ValueError, match="Maximum distance"):
        retrieve_relevant_documents(
            query="Why did my payment fail?",
            max_distance=2.5,
        )