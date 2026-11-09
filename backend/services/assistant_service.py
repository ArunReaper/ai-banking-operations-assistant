
import re

from sqlalchemy.orm import Session

from backend.services.llm_service import generate_response
from backend.services.transaction_service import get_transaction_details


def answer_transaction_question(
        db: Session,
        user_message: str,
) -> str:
    """Answer a transaction-related question using verified database data."""

    if not user_message.strip():
        raise ValueError("Please enter a question.")

    # Extract the transaction reference from the user's question.
    match = re.search(
        r"\bTXN[A-Z0-9]{8,}\b",
        user_message,
        re.IGNORECASE,
    )

    if not match:
        raise ValueError(
            "Please include a transaction reference, "
            "for example TXNCA3E179933CA461C."
        )

    transaction_reference = match.group(0).upper()

    # Retrieve transaction information from PostgreSQL.
    transaction = get_transaction_details(
        db,
        transaction_reference,
    )

    if transaction is None:
        raise ValueError(
            f"Transaction {transaction_reference} was not found."
        )

    # Include only the information needed for the investigation.
    transaction_context = {
        "transaction_reference": transaction["transaction_reference"],
        "amount": transaction["amount"],
        "currency": transaction["currency"],
        "transaction_type": transaction["transaction_type"],
        "payment_channel": transaction["payment_channel"],
        "transaction_status": transaction["transaction_status"],
        "failure_code": transaction["failure_code"],
        "failure_reason": transaction["failure_reason"],
        "account_balance": transaction["balance"],
        "account_status": transaction["account_status"],
        "customer_kyc_status": transaction["kyc_status"],
        "customer_status": transaction["customer_status"],
    }

    prompt = f"""
You are an AI assistant supporting a bank's operations team.

Your task is to help investigate banking transactions.

Use the transaction data below as the source of truth.

TRANSACTION DATA:
{transaction_context}

OPERATIONS EMPLOYEE QUESTION:
{user_message}

INSTRUCTIONS:
1. Explain the transaction status and recorded failure reason.
2. Distinguish verified database facts from possible explanations.
3. Do not invent banking policies, transaction events, or system logs.
4. Do not claim that a payment was refunded, reversed, or resolved
   unless the supplied data explicitly confirms it.
5. If the current account balance appears inconsistent with the
   recorded failure reason, point this out. The current balance
   does not necessarily represent the available balance at the
   time of the transaction.
6. Suggest practical investigation steps, but do not initiate
   any banking operation.
7. Use clear, professional language suitable for a banking
   operations employee.

Structure your answer using:
- Transaction summary
- What the data tells us
- Possible explanation or unresolved questions
- Recommended investigation steps

Remember: You are providing investigation assistance, not
making or executing banking decisions.
"""

    return generate_response(
        prompt=prompt,
        temperature=0.2,
        max_output_tokens=1500,
    )
