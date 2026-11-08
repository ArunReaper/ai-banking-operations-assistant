import pytest
from backend.api.main import app
from backend.database.connection import SessionLocal, get_db
from fastapi.testclient import TestClient
from sqlalchemy import text


@pytest.fixture
def client():
    """Create a test client with a PostgreSQL database session."""

    def override_get_db():
        db = SessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


def get_existing_transaction_reference():
    """Retrieve a transaction reference from synthetic test data."""
    with SessionLocal() as db:
        return db.execute(
            text("""
                SELECT transaction_reference
                FROM transactions
                LIMIT 1
            """)
        ).scalar_one()


def get_customer_with_multiple_transactions():
    """Retrieve a customer with at least five transactions."""
    with SessionLocal() as db:
        return db.execute(
            text("""
                SELECT a.customer_id
                FROM accounts a
                JOIN transactions t
                    ON a.account_id = t.account_id
                GROUP BY a.customer_id
                HAVING COUNT(*) >= 5
                LIMIT 1
            """)
        ).scalar_one()


def test_transaction_lookup_success(client):
    """Verify that a valid transaction returns HTTP 200."""
    reference = get_existing_transaction_reference()

    response = client.get(
        f"/api/v1/transactions/{reference}"
    )

    assert response.status_code == 200
    assert response.json()["transaction_reference"] == reference
    assert "email" not in response.json()


def test_transaction_lookup_not_found(client):
    """Verify that an unknown transaction returns HTTP 404."""
    response = client.get(
        "/api/v1/transactions/INVALID-REFERENCE-123"
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Transaction not found."


def test_customer_transaction_history(client):
    """Verify that customer transaction history is returned."""
    customer_id = get_customer_with_multiple_transactions()

    response = client.get(
        f"/api/v1/customers/{customer_id}/transactions"
    )

    assert response.status_code == 200
    assert len(response.json()) >= 5


def test_customer_transaction_history_limit(client):
    """Verify that the requested transaction limit is respected."""
    customer_id = get_customer_with_multiple_transactions()

    response = client.get(
        f"/api/v1/customers/{customer_id}/transactions",
        params={"limit": 5},
    )

    assert response.status_code == 200
    assert len(response.json()) == 5


def test_customer_transaction_history_invalid_limit(client):
    """Verify that an invalid transaction limit returns HTTP 422."""
    customer_id = get_customer_with_multiple_transactions()

    response = client.get(
        f"/api/v1/customers/{customer_id}/transactions",
        params={"limit": 101},
    )

    assert response.status_code == 422