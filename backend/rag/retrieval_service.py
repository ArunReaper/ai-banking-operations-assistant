
from typing import Any

from backend.rag.vector_store import (
    get_chroma_collection,
    search_similar_chunks,
)

DEFAULT_MAX_DISTANCE = 0.65

def retrieve_relevant_documents(
        query: str,
        n_results: int = 3,
        max_distance: float = DEFAULT_MAX_DISTANCE,
) -> list[dict[str, Any]]:
    """
    Retrieve SOP chunks and filter out results above the
    configured cosine-distance threshold.
    """

    if not query or not query.strip():
        raise ValueError("Query cannot be empty.")

    if n_results <= 0:
        raise ValueError("Number of results must be positive.")

    if not 0.0 <= max_distance <= 2.0:
        raise ValueError("Maximum distance must be between 0 and 2.")

    collection = get_chroma_collection()

    results = search_similar_chunks(
        collection=collection,
        query=query,
        n_results=n_results,
    )

    relevant_results = [
        result
        for result in results
        if result["distance"] <= max_distance
    ]

    return [
        {
            "content": result["content"],
            "source": result["metadata"].get("source"),
            "title": result["metadata"].get("title"),
            "document_id": result["metadata"].get("document_id"),
            "version": result["metadata"].get("version"),
            "distance": result["distance"],
        }
        for result in relevant_results
    ]