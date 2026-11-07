from backend.database.connection import SessionLocal
from backend.services.transaction_service import (
    get_recent_transactions,
    get_transaction_details,
)
from sqlalchemy import text


def test_get_transaction_details():
    """Verify transaction retrieval with associated account and customer data."""
    with SessionLocal() as db:
        transaction_reference = db.execute(
            text("""
                SELECT transaction_reference
                FROM transactions
                LIMIT 1
            """)
        ).scalar_one()

        result = get_transaction_details(db, transaction_reference)

    assert result is not None
    assert result["transaction_reference"] == transaction_reference
    assert result["transaction_id"] is not None
    assert result["account_id"] is not None
    assert result["customer_id"] is not None
    assert result["first_name"] is not None
    assert result["account_number"] is not None


def test_get_transaction_details_not_found():
    """Verify that an unknown transaction reference returns None."""
    with SessionLocal() as db:
        result = get_transaction_details(
            db,
            "TXN-DOES-NOT-EXIST",
        )

    assert result is None


    def test_get_recent_transactions():
        """Verify retrieval of a customer's recent transactions."""
    with SessionLocal() as db:
        customer_id = db.execute(
            text("""
                SELECT customer_id
                FROM customers
                WHERE customer_id IN (
                    SELECT a.customer_id
                    FROM accounts a
                    JOIN transactions t
                        ON a.account_id = t.account_id
                )
                LIMIT 1
            """)
        ).scalar_one()

        result = get_recent_transactions(db, str(customer_id), limit=5)

    assert len(result) <= 5

    for transaction in result:
        assert transaction["transaction_reference"] is not None
        assert transaction["account_number"] is not None
        assert transaction["amount"] > 0


def test_get_recent_transactions():
    """Verify retrieval of a customer's recent transactions."""
    with SessionLocal() as db:
        customer_id = db.execute(
            text("""
                SELECT customer_id
                FROM customers
                WHERE customer_id IN (
                    SELECT a.customer_id
                    FROM accounts a
                    JOIN transactions t
                        ON a.account_id = t.account_id
                )
                LIMIT 1
            """)
        ).scalar_one()

        result = get_recent_transactions(db, str(customer_id), limit=5)

    assert len(result) <= 5

    for transaction in result:
        assert transaction["transaction_reference"] is not None
        assert transaction["account_number"] is not None
        assert transaction["amount"] > 0


def test_get_recent_transactions_invalid_limit():
    """Verify that invalid transaction limits are rejected."""
    with SessionLocal() as db:
        try:
            get_recent_transactions(db, "test-customer-id", limit=101)
            assert False, "Expected ValueError was not raised."
        except ValueError as error:
            assert str(error) == "Limit must be between 1 and 100."