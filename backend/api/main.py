from uuid import UUID

from fastapi import Depends, FastAPI, HTTPException, Query, status
from sqlalchemy.orm import Session

from backend.api.schemas import (
    TransactionDetailsResponse,
    TransactionSummaryResponse,
)
from backend.database.connection import get_db
from backend.services.transaction_service import (
    get_recent_transactions,
    get_transaction_details,
)

app = FastAPI(
    title="AI Banking Operations Assistant",
    description=(
        "APIs for investigating banking transactions "
        "and retrieving customer transaction history."
    ),
    version="0.1.0",
)


@app.get("/health")
def health_check():
    """Check whether the API application is running."""
    return {
        "status": "healthy",
        "application": "AI Banking Operations Assistant",
    }


@app.get(
    "/api/v1/transactions/{transaction_reference}",
    response_model=TransactionDetailsResponse,
    summary="Get transaction details",
)
def get_transaction(
        transaction_reference: str,
        db: Session = Depends(get_db),
):
    """Retrieve transaction, account and customer details."""

    transaction = get_transaction_details(
        db,
        transaction_reference,
    )

    if transaction is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transaction not found.",
        )

    return transaction

@app.get(
    "/api/v1/customers/{customer_id}/transactions",
    response_model=list[TransactionSummaryResponse],
    summary="Get customer transaction history",
)
def get_customer_transactions(
        customer_id: UUID,
        db: Session = Depends(get_db),
        limit: int = Query(default=10, ge=1, le=100),
):
    """Retrieve a customer's most recent transactions."""

    transactions = get_recent_transactions(
        db,
        str(customer_id),
        limit,
    )

    return transactions