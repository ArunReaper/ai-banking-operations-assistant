
from unittest.mock import MagicMock, patch

from backend.agent.graph import assistant_graph
from backend.agent.state import create_initial_state


@patch("backend.agent.graph.lookup_transaction")
def test_graph_routes_transaction_request(mock_lookup):
    expected_data = {
        "transaction_reference": "TXNCA3E179933CA461C",
        "transaction_status": "FAILED",
        "failure_code": "INSUFFICIENT_FUNDS",
    }

    mock_lookup.return_value = {
        "success": True,
        "error": None,
        "data": expected_data,
    }

    state = create_initial_state(
        "Why did transaction TXNCA3E179933CA461C fail?"
    )

    db = MagicMock()

    result = assistant_graph.invoke(
        state,
        config={"configurable": {"db": db}},
    )

    assert result["intent"] == "transaction"
    assert result["transaction_reference"] == "TXNCA3E179933CA461C"
    assert result["transaction_data"] == expected_data
    assert result["error"] is None
    assert "retrieved successfully" in result["response"]

    mock_lookup.assert_called_once_with(
        db=db,
        transaction_reference="TXNCA3E179933CA461C",
    )


@patch("backend.agent.graph.lookup_transaction")
def test_graph_handles_transaction_not_found(mock_lookup):
    mock_lookup.return_value = {
        "success": False,
        "error": "No transaction found for reference TXNCA3E179933CA461C.",
        "data": None,
    }

    state = create_initial_state(
        "Why did transaction TXNCA3E179933CA461C fail?"
    )

    result = assistant_graph.invoke(
        state,
        config={"configurable": {"db": MagicMock()}},
    )

    assert result["intent"] == "transaction"
    assert result["transaction_data"] is None
    assert "No transaction found" in result["response"]
    assert result["error"] is not None


def test_graph_routes_account_request():
    customer_id = "12345678-1234-1234-1234-123456789012"

    state = create_initial_state(
        f"Show the account status for customer {customer_id}"
    )

    result = assistant_graph.invoke(state)

    assert result["intent"] == "account"
    assert result["customer_id"] == customer_id
    assert "account investigation" in result["response"]


def test_graph_routes_missing_reference_to_clarification():
    state = create_initial_state("Why did my payment fail?")

    result = assistant_graph.invoke(state)

    assert result["intent"] == "clarification"
    assert "transaction reference" in result["response"]


def test_graph_routes_unsupported_request_to_fallback():
    state = create_initial_state("What is the weather in Mumbai?")

    result = assistant_graph.invoke(state)

    assert result["intent"] == "fallback"
    assert "currently assist" in result["response"]