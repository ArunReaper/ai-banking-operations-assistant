
from unittest.mock import MagicMock

import pytest
from backend.services import assistant_service


@pytest.fixture
def mock_transaction():
    """Return a sample transaction record."""
    return {
        "transaction_reference": "TXN1234567890",
        "amount": 1500.00,
        "currency": "INR",
        "transaction_type": "DEBIT",
        "payment_channel": "UPI",
        "transaction_status": "FAILED",
        "failure_code": "INSUFFICIENT_FUNDS",
        "failure_reason": "Insufficient funds",
        "balance": 500.00,
        "account_status": "ACTIVE",
        "kyc_status": "VERIFIED",
        "customer_status": "ACTIVE",
    }


def test_successful_assistant_response(monkeypatch, mock_transaction):
    """Test the complete flow with transaction data and retrieved SOPs."""

    db = MagicMock()

    monkeypatch.setattr(
        assistant_service,
        "get_transaction_details",
        lambda db, reference: mock_transaction,
    )

    monkeypatch.setattr(
        assistant_service,
        "retrieve_relevant_documents",
        lambda query, n_results: [
            {
                "content": "Verify the transaction status and investigate the failure.",
                "title": "UPI Failure Handling",
                "document_id": "SOP-UPI-001",
                "version": "1.0",
                "source": "upi_failure_handling.md",
                "distance": 0.25,
            }
        ],
    )

    captured_prompt = {}

    def mock_generate_response(prompt, temperature, max_output_tokens):
        captured_prompt["prompt"] = prompt
        return "The transaction failed due to insufficient funds."

    monkeypatch.setattr(
        assistant_service,
        "generate_response",
        mock_generate_response,
    )

    response = assistant_service.answer_transaction_question(
        db,
        "Why did transaction TXN1234567890 fail?",
    )

    assert response == "The transaction failed due to insufficient funds."
    assert "TXN1234567890" in captured_prompt["prompt"]
    assert "SOP-UPI-001" in captured_prompt["prompt"]
    assert "synthetic demonstration" in captured_prompt["prompt"].lower()


def test_assistant_without_retrieved_documents(monkeypatch, mock_transaction):
    """Test that the assistant handles an empty RAG result."""

    db = MagicMock()

    monkeypatch.setattr(
        assistant_service,
        "get_transaction_details",
        lambda db, reference: mock_transaction,
    )

    monkeypatch.setattr(
        assistant_service,
        "retrieve_relevant_documents",
        lambda query, n_results: [],
    )

    captured_prompt = {}

    def mock_generate_response(prompt, temperature, max_output_tokens):
        captured_prompt["prompt"] = prompt
        return "The transaction failed. Further investigation is required."

    monkeypatch.setattr(
        assistant_service,
        "generate_response",
        mock_generate_response,
    )

    response = assistant_service.answer_transaction_question(
        db,
        "Explain transaction TXN1234567890.",
    )

    assert "further investigation" in response.lower()
    assert "No relevant operational guidance was retrieved" in (
        captured_prompt["prompt"]
    )


def test_transaction_not_found_does_not_call_llm(monkeypatch):
    """Test that a missing transaction stops processing."""

    db = MagicMock()
    llm_called = False

    monkeypatch.setattr(
        assistant_service,
        "get_transaction_details",
        lambda db, reference: None,
    )

    def mock_generate_response(**kwargs):
        nonlocal llm_called
        llm_called = True
        return "Unexpected response"

    monkeypatch.setattr(
        assistant_service,
        "generate_response",
        mock_generate_response,
    )

    with pytest.raises(ValueError, match="was not found"):
        assistant_service.answer_transaction_question(
            db,
            "Explain transaction TXN1234567890.",
        )

    assert llm_called is False


def test_question_without_transaction_reference():
    """Test that a transaction reference is mandatory."""

    db = MagicMock()

    with pytest.raises(ValueError, match="transaction reference"):
        assistant_service.answer_transaction_question(
            db,
            "Why did the payment fail?",
        )