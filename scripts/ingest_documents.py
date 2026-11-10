from backend.rag.chunker import create_document_chunks
from backend.rag.document_loader import load_markdown_documents
from backend.rag.vector_store import (
    add_document_chunks,
    get_chroma_collection,
)


def ingest_documents() -> None:
    """Load, chunk, embed and store all Markdown SOP documents."""

    print("Starting document ingestion...")

    # Step 1: Load source documents.
    documents = load_markdown_documents()
    print(f"Documents loaded: {len(documents)}")

    if not documents:
        print("No documents found. Nothing to ingest.")
        return

    # Step 2: Split documents into smaller chunks.
    chunks = create_document_chunks(
        documents,
        chunk_size=1000,
        chunk_overlap=150,
    )
    print(f"Chunks generated: {len(chunks)}")

    # Step 3: Create or retrieve the persistent collection.
    collection = get_chroma_collection()
    print(f"ChromaDB collection: {collection.name}")

    # Remove existing chunks before re-ingesting the current documents.
    if collection.count() > 0:
        collection.delete(
            ids=collection.get()["ids"]
        )

    stored_count = add_document_chunks(collection, chunks)

    print(f"Chunks processed: {stored_count}")
    print(f"Total chunks in collection: {collection.count()}")
    print("Document ingestion completed successfully.")


if __name__ == "__main__":
    ingest_documents()
