
import re

from sqlalchemy.orm import Session

from backend.services.transaction_service import get_transaction_details

TRANSACTION_REFERENCE_PATTERN = re.compile(
    r"^TXN[A-Z0-9]{8,}$",
    re.IGNORECASE,
)


def lookup_transaction(
        db: Session,
        transaction_reference: str,
) -> dict:
    """
    Retrieve transaction details through the existing banking service.

    This tool is read-only and does not execute model-generated SQL.
    """
    transaction_reference = transaction_reference.strip().upper()

    if not TRANSACTION_REFERENCE_PATTERN.fullmatch(
            transaction_reference
    ):
        return {
            "success": False,
            "error": "Invalid transaction reference format.",
            "data": None,
        }

    transaction = get_transaction_details(
        db=db,
        transaction_reference=transaction_reference,
    )

    if transaction is None:
        return {
            "success": False,
            "error": (
                f"No transaction found for reference "
                f"{transaction_reference}."
            ),
            "data": None,
        }

    return {
        "success": True,
        "error": None,
        "data": transaction,
    }
