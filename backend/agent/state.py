
from typing import Any, Literal, TypedDict


class AgentState(TypedDict):
    """Shared state passed between banking assistant graph nodes."""

    # Original user request
    question: str

    # Request classification
    intent: Literal[
                "transaction",
                "account",
                "clarification",
                "fallback",
            ] | None

    # Identifiers extracted from the request
    customer_id: str | None
    transaction_reference: str | None

    # Retrieved banking information
    transaction_data: dict[str, Any] | None
    customer_data: dict[str, Any] | None

    # Retrieved operational guidance
    policy_context: list[dict[str, Any]]

    # Validation and execution information
    warnings: list[str]
    response: str | None
    error: str | None


def create_initial_state(question: str) -> AgentState:
    """Create an initial state for a new assistant request."""

    return {
        "question": question,
        "intent": None,
        "customer_id": None,
        "transaction_reference": None,
        "transaction_data": None,
        "customer_data": None,
        "policy_context": [],
        "warnings": [],
        "response": None,
        "error": None,
    }
