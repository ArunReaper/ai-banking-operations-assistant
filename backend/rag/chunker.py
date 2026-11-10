import hashlib
import re
from typing import Any


def split_into_chunks(
        text: str,
        chunk_size: int = 1000,
        chunk_overlap: int = 150,
) -> list[str]:
    """Split text into overlapping chunks, preferring natural boundaries."""

    if chunk_size <= 0:
        raise ValueError("Chunk size must be positive.")

    if chunk_overlap < 0 or chunk_overlap >= chunk_size:
        raise ValueError(
            "Chunk overlap must be non-negative and smaller than chunk size."
        )

    text = text.strip()

    if not text:
        return []

    if len(text) <= chunk_size:
        return [text]

    if chunk_overlap < 0 or chunk_overlap >= chunk_size:
        raise ValueError(
            "Chunk overlap must be non-negative and smaller than chunk size."
        )

    chunks = []
    start = 0

    while start < len(text):
        end = min(start + chunk_size, len(text))

        if end < len(text):
            boundary = text.rfind("\n\n", start, end)

            if boundary == -1 or boundary <= start + chunk_size // 2:
                boundary = text.rfind(". ", start, end)

            if boundary > start + chunk_size // 2:
                end = boundary + 1

        chunk = text[start:end].strip()

        if chunk:
            chunks.append(chunk)

        if end >= len(text):
            break

        next_start = max(start + 1, end - chunk_overlap)

        # Move to a nearby whitespace boundary when one exists.
        # Otherwise, retain the calculated overlap.
        whitespace_match = re.search(r"\s", text[next_start:end])

        if whitespace_match:
            next_start += whitespace_match.start() + 1

        start = next_start

    return chunks


def create_document_chunks(
        documents: list[dict[str, Any]],
        chunk_size: int = 1000,
        chunk_overlap: int = 150,
) -> list[dict[str, Any]]:
    """Convert loaded documents into chunks with metadata and stable IDs."""

    chunked_documents = []

    for document in documents:
        content = document["content"]
        metadata = document["metadata"]

        chunks = split_into_chunks(
            content,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
        )

        for index, chunk in enumerate(chunks):
            chunk_id_source = (
                f"{metadata.get('document_id', metadata['source'])}:"
                f"{index}:{chunk}"
            )

            chunk_id = hashlib.sha256(
                chunk_id_source.encode("utf-8")
            ).hexdigest()

            chunked_documents.append(
                {
                    "id": chunk_id,
                    "content": chunk,
                    "metadata": {
                        **metadata,
                        "chunk_index": index,
                    },
                }
            )

    return chunked_documents