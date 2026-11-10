from backend.rag.vector_store import (
    get_chroma_collection,
    search_similar_chunks,
)


def main() -> None:
    collection = get_chroma_collection()

    queries = [
        "Why might an IMPS payment time out?",
        "How should operations investigate an insufficient funds failure?",
        "Can we confirm a refund when a transaction is still pending?",
    ]

    for query in queries:
        print(f"\n{'=' * 80}")
        print(f"QUERY: {query}")
        print("=" * 80)

        results = search_similar_chunks(
            collection=collection,
            query=query,
            n_results=3,
        )

        for index, result in enumerate(results, start=1):
            metadata = result["metadata"]

            print(f"\nResult {index}")
            print(f"Document: {metadata.get('title')}")
            print(f"Document ID: {metadata.get('document_id')}")
            print(f"Distance: {result['distance']:.4f}")
            print(f"Content:\n{result['content']}")


if __name__ == "__main__":
    main()