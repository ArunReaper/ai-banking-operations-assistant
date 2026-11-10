
from backend.agent.classifier import classify_request
from backend.agent.state import create_initial_state


def test_classifies_transaction_with_reference():
    state = create_initial_state(
        "Why did transaction TXNCA3E179933CA461C fail?"
    )

    result = classify_request(state)

    assert result["intent"] == "transaction"
    assert result["transaction_reference"] == "TXNCA3E179933CA461C"


def test_requests_transaction_reference_when_missing():
    state = create_initial_state("Why did my payment fail?")

    result = classify_request(state)

    assert result["intent"] == "clarification"
    assert "transaction reference" in result["error"]


def test_classifies_account_request_with_customer_id():
    customer_id = "12345678-1234-1234-1234-123456789012"
    state = create_initial_state(
        f"Show the account status for customer {customer_id}"
    )

    result = classify_request(state)

    assert result["intent"] == "account"
    assert result["customer_id"] == customer_id


def test_requests_customer_id_for_account_request():
    state = create_initial_state("What is my account balance?")

    result = classify_request(state)

    assert result["intent"] == "clarification"
    assert "customer ID" in result["error"]


def test_routes_unsupported_question_to_fallback():
    state = create_initial_state("What is the weather in Mumbai?")

    result = classify_request(state)

    assert result["intent"] == "fallback"