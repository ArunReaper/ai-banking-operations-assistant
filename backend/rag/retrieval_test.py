from backend.rag.retrieval_service import retrieve_relevant_documents


def main() -> None:

    queries = [
        # Relevant queries
        "Why might an IMPS payment time out?",
        "How should operations investigate an insufficient funds failure?",
        "Can we confirm a refund when a transaction is still pending?",

        # Related but less specific queries
        "What should operations check when a payment fails?",
        "How do we investigate a frozen bank account?",

        # Unrelated queries
        "What is the weather in Mumbai today?",
        "How can I apply for a home loan?",
    ]

    for query in queries:
        print("\n" + "=" * 80)
        print(f"QUERY: {query}")
        print("=" * 80)

        results = retrieve_relevant_documents(
            query=query,
            n_results=3,
        )

        if not results:
            print("No relevant operational guidance found.")
            continue

        for index, result in enumerate(results, start=1):
            print(f"\nResult {index}")
            print(f"Document: {result['title']}")
            print(f"Document ID: {result['document_id']}")
            print(f"Distance: {result['distance']:.4f}")
            print(f"Content:\n{result['content']}")

if __name__ == "__main__":
    main()