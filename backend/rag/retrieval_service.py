
from typing import Any

from backend.rag.vector_store import (
    get_chroma_collection,
    search_similar_chunks,
)


def retrieve_relevant_documents(
        query: str,
        n_results: int = 3,
) -> list[dict[str, Any]]:
    """
    Retrieve relevant SOP chunks for a natural-language query.

    Returns the document content, source metadata and vector distance.
    """

    if not query or not query.strip():
        raise ValueError("Query cannot be empty.")

    if n_results <= 0:
        raise ValueError("Number of results must be positive.")

    collection = get_chroma_collection()

    results = search_similar_chunks(
        collection=collection,
        query=query,
        n_results=n_results,
    )

    return [
        {
            "content": result["content"],
            "source": result["metadata"].get("source"),
            "title": result["metadata"].get("title"),
            "document_id": result["metadata"].get("document_id"),
            "version": result["metadata"].get("version"),
            "distance": result["distance"],
        }
        for result in results
    ]