from pathlib import Path
from typing import Any

import chromadb
from chromadb.api.models.Collection import Collection

from backend.rag.embedding_service import generate_embeddings

PROJECT_ROOT = Path(__file__).resolve().parents[2]

DEFAULT_CHROMA_DIR = PROJECT_ROOT / "data" / "chroma"

COLLECTION_NAME = "banking_operations_sops"


def get_chroma_collection(
    persist_directory: Path = DEFAULT_CHROMA_DIR,
) -> Collection:
    """Create or retrieve the persistent ChromaDB collection."""

    persist_directory.mkdir(parents=True, exist_ok=True)

    client = chromadb.PersistentClient(
        path=str(persist_directory)
    )

    collection = client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},
    )

    return collection


def add_document_chunks(
    collection: Collection,
    chunks: list[dict[str, Any]],
) -> int:
    """Generate embeddings and upsert document chunks into ChromaDB."""

    if not chunks:
        return 0

    contents = [chunk["content"] for chunk in chunks]
    embeddings = generate_embeddings(contents)

    collection.upsert(
        ids=[chunk["id"] for chunk in chunks],
        documents=contents,
        metadatas=[chunk["metadata"] for chunk in chunks],
        embeddings=embeddings,
    )

    return len(chunks)


def search_similar_chunks(
    collection: Collection,
    query: str,
    n_results: int = 3,
) -> list[dict[str, Any]]:
    """Retrieve the most semantically similar document chunks."""

    if not query or not query.strip():
        raise ValueError("Search query cannot be empty.")

    if n_results <= 0:
        raise ValueError("Number of results must be positive.")

    collection_size = collection.count()

    if collection_size == 0:
        return []

    query_embedding = generate_embeddings([query])

    results = collection.query(
        query_embeddings=query_embedding,
        n_results=min(n_results, collection_size),
        include=["documents", "metadatas", "distances"],
    )

    retrieved_chunks = []

    for index, document in enumerate(results["documents"][0]):
        retrieved_chunks.append(
            {
                "content": document,
                "metadata": results["metadatas"][0][index],
                "distance": results["distances"][0][index],
            }
        )

    return retrieved_chunks
