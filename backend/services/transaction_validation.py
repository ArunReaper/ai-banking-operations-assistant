from typing import Any


def validate_transaction_consistency(
        transaction: dict[str, Any],
) -> list[str]:
    """
    Identify potential inconsistencies in transaction data.

    These checks generate investigation warnings. They do not
    independently establish the actual cause of a transaction failure.
    """

    warnings = []

    transaction_type = transaction.get("transaction_type")
    failure_code = transaction.get("failure_code")
    status = transaction.get("status")
    failure_reason = transaction.get("failure_reason")
    account_status = transaction.get("account_status")

    if (
            transaction_type == "CREDIT"
            and failure_code == "INSUFFICIENT_FUNDS"
    ):
        warnings.append(
            "INSUFFICIENT_FUNDS is unusual for a CREDIT transaction. "
            "Verify whether the failure relates to the source/debit account "
            "or an underlying processing step. Do not attribute it to the "
            "receiving customer's balance."
        )

    if (
            failure_code == "ACCOUNT_FROZEN"
            and account_status == "ACTIVE"
    ):
        warnings.append(
            "The recorded failure code indicates an account-frozen "
            "condition, but the account is currently ACTIVE. Verify the "
            "account status at the transaction timestamp."
        )

    if status == "FAILED" and not failure_code and not failure_reason:
        warnings.append(
            "The transaction is marked FAILED but has no recorded "
            "failure code or failure reason. Further investigation is needed."
        )

    return warnings