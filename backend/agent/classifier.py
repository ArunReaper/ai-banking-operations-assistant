
import re

from backend.agent.state import AgentState

TRANSACTION_REFERENCE_PATTERN = re.compile(
    r"\bTXN[A-Z0-9]{8,}\b",
    re.IGNORECASE,
)

CUSTOMER_ID_PATTERN = re.compile(
    r"\b[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-"
    r"[0-9a-f]{4}-[0-9a-f]{12}\b",
    re.IGNORECASE,
)

TRANSACTION_KEYWORDS = (
    "transaction",
    "payment",
    "transfer",
    "upi",
    "imps",
    "neft",
    "rtgs",
    "failed",
    "failure",
)

ACCOUNT_KEYWORDS = (
    "account",
    "balance",
    "account status",
)


def classify_request(state: AgentState) -> dict:
    """Classify a banking operations question using deterministic rules."""

    question = state["question"].strip()
    normalized_question = question.lower()

    transaction_match = TRANSACTION_REFERENCE_PATTERN.search(question)

    if transaction_match:
        return {
            "intent": "transaction",
            "transaction_reference": transaction_match.group(0).upper(),
        }

    customer_match = CUSTOMER_ID_PATTERN.search(question)

    if any(keyword in normalized_question for keyword in ACCOUNT_KEYWORDS):
        if customer_match:
            return {
                "intent": "account",
                "customer_id": customer_match.group(0),
            }

        return {
            "intent": "clarification",
            "error": "Please provide a valid customer ID to investigate the account.",
        }

    if any(keyword in normalized_question for keyword in TRANSACTION_KEYWORDS):
        return {
            "intent": "clarification",
            "error": (
                "Please include a transaction reference, "
                "for example TXNCA3E179933CA461C."
            ),
        }

    return {
        "intent": "fallback",
        "error": "I can currently assist with banking transaction and account investigations.",
    }