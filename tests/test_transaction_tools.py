
from unittest.mock import MagicMock, patch

from backend.tools.transaction_tools import lookup_transaction


@patch("backend.tools.transaction_tools.get_transaction_details")
def test_lookup_transaction_success(mock_get_transaction):
    expected_data = {
        "transaction_reference": "TXN12345678",
        "transaction_status": "FAILED",
    }
    mock_get_transaction.return_value = expected_data

    db = MagicMock()

    result = lookup_transaction(db, "TXN12345678")

    assert result["success"] is True
    assert result["error"] is None
    assert result["data"] == expected_data

    mock_get_transaction.assert_called_once_with(
        db=db,
        transaction_reference="TXN12345678",
    )


@patch("backend.tools.transaction_tools.get_transaction_details")
def test_lookup_transaction_not_found(mock_get_transaction):
    mock_get_transaction.return_value = None

    result = lookup_transaction(
        MagicMock(),
        "TXN12345678",
    )

    assert result["success"] is False
    assert result["data"] is None
    assert "No transaction found" in result["error"]


@patch("backend.tools.transaction_tools.get_transaction_details")
def test_lookup_transaction_invalid_reference(mock_get_transaction):
    result = lookup_transaction(
        MagicMock(),
        "INVALID123",
    )

    assert result["success"] is False
    assert result["data"] is None
    assert "Invalid transaction reference" in result["error"]

    mock_get_transaction.assert_not_called()


@patch("backend.tools.transaction_tools.get_transaction_details")
def test_lookup_transaction_normalizes_reference(mock_get_transaction):
    mock_get_transaction.return_value = {
        "transaction_reference": "TXN12345678",
    }

    result = lookup_transaction(
        MagicMock(),
        "txn12345678",
    )

    assert result["success"] is True

    mock_get_transaction.assert_called_once_with(
        db=mock_get_transaction.call_args.kwargs["db"],
        transaction_reference="TXN12345678",
    )
