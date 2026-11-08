from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel


class TransactionDetailsResponse(BaseModel):
    transaction_id: UUID
    transaction_reference: str
    amount: Decimal
    currency: str
    transaction_type: str
    payment_channel: str
    transaction_status: str
    failure_code: str | None
    failure_reason: str | None
    merchant_name: str | None
    counterparty_reference: str | None
    transaction_timestamp: datetime

    account_id: UUID
    account_number: str
    account_type: str
    balance: Decimal
    account_status: str

    customer_id: UUID
    first_name: str
    last_name: str
    kyc_status: str
    customer_status: str

class TransactionSummaryResponse(BaseModel):
    transaction_id: UUID
    transaction_reference: str
    amount: Decimal
    currency: str
    transaction_type: str
    payment_channel: str
    transaction_status: str
    failure_code: str | None
    failure_reason: str | None
    merchant_name: str | None
    transaction_timestamp: datetime
    account_number: str
    account_type: str