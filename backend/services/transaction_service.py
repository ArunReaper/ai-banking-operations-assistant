from sqlalchemy import text
from sqlalchemy.orm import Session


def get_transaction_details(
        db: Session,
        transaction_reference: str,
) -> dict | None:
    """
    Retrieve transaction details along with associated account
    and customer information.
    """

    query = text("""
        SELECT
            t.transaction_id,
            t.transaction_reference,
            t.amount,
            t.currency,
            t.transaction_type,
            t.payment_channel,
            t.transaction_status,
            t.failure_code,
            t.failure_reason,
            t.merchant_name,
            t.counterparty_reference,
            t.transaction_timestamp,

            a.account_id,
            a.account_number,
            a.account_type,
            a.balance,
            a.account_status,

            c.customer_id,
            c.first_name,
            c.last_name,
            c.email,
            c.kyc_status,
            c.customer_status

        FROM transactions t

        JOIN accounts a
            ON t.account_id = a.account_id

        JOIN customers c
            ON a.customer_id = c.customer_id

        WHERE t.transaction_reference = :transaction_reference
    """)

    result = db.execute(
        query,
        {"transaction_reference": transaction_reference},
    )

    row = result.mappings().first()

    if row is None:
        return None

    return dict(row)

def get_recent_transactions(
        db: Session,
        customer_id: str,
        limit: int = 10,
) -> list[dict]:
    """
    Retrieve a customer's most recent transactions.

    Transactions are ordered from newest to oldest.
    """

    if limit < 1 or limit > 100:
        raise ValueError("Limit must be between 1 and 100.")

    query = text("""
        SELECT
            t.transaction_id,
            t.transaction_reference,
            t.amount,
            t.currency,
            t.transaction_type,
            t.payment_channel,
            t.transaction_status,
            t.failure_code,
            t.failure_reason,
            t.merchant_name,
            t.transaction_timestamp,
            a.account_number,
            a.account_type
        FROM transactions t
        JOIN accounts a
            ON t.account_id = a.account_id
        WHERE a.customer_id = :customer_id
        ORDER BY t.transaction_timestamp DESC
        LIMIT :limit
    """)

    result = db.execute(
        query,
        {
            "customer_id": customer_id,
            "limit": limit,
            },
        )

    return [dict(row) for row in result.mappings().all()]