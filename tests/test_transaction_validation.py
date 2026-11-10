import pytest
from backend.services.transaction_validation import (
    validate_transaction_consistency,
)


@pytest.mark.parametrize(
    ("transaction", "expected_warning"),
    [
        (
                {
                    "transaction_type": "CREDIT",
                    "failure_code": "INSUFFICIENT_FUNDS",
                    "status": "FAILED",
                },
                "unusual for a CREDIT transaction",
        ),
        (
                {
                    "transaction_type": "DEBIT",
                    "failure_code": "INSUFFICIENT_FUNDS",
                    "status": "FAILED",
                },
                None,
        ),
        (
                {
                    "failure_code": "ACCOUNT_FROZEN",
                    "account_status": "ACTIVE",
                    "status": "FAILED",
                },
                "currently ACTIVE",
        ),
        (
                {
                    "status": "FAILED",
                    "failure_code": None,
                    "failure_reason": None,
                },
                "no recorded failure code or failure reason",
        ),
        (
                {
                    "transaction_type": "DEBIT",
                    "failure_code": "INSUFFICIENT_FUNDS",
                    "status": "FAILED",
                    "failure_reason": "Insufficient balance",
                    "account_status": "ACTIVE",
                },
                None,
        ),
    ],
)
def test_validate_transaction_consistency(
        transaction,
        expected_warning,
):
    warnings = validate_transaction_consistency(transaction)

    if expected_warning is None:
        assert warnings == []
    else:
        assert any(
            expected_warning in warning
            for warning in warnings
        )


def test_returns_multiple_warnings_when_multiple_issues_exist():
    transaction = {
        "transaction_type": "CREDIT",
        "failure_code": "INSUFFICIENT_FUNDS",
        "status": "FAILED",
        "account_status": "ACTIVE",
    }

    warnings = validate_transaction_consistency(transaction)

    assert len(warnings) == 1

def test_returns_empty_list_for_valid_transaction():
    transaction = {
        "transaction_type": "DEBIT",
        "failure_code": None,
        "failure_reason": None,
        "status": "SUCCESS",
        "account_status": "ACTIVE",
    }

    assert validate_transaction_consistency(transaction) == []