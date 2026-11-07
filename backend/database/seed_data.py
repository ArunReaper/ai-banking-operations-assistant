import random
import uuid
from datetime import UTC
from decimal import Decimal

from faker import Faker
from sqlalchemy import text

from backend.database.connection import engine

# ---------------------------------------------------------
# 2. REPRODUCIBLE DATA GENERATION
# ---------------------------------------------------------

RANDOM_SEED = 42

random.seed(RANDOM_SEED)

fake = Faker("en_IN")
Faker.seed(RANDOM_SEED)

# ---------------------------------------------------------
# 3. DATABASE CONNECTION
# ---------------------------------------------------------

def test_database_connection() -> None:
    """Verify connectivity to the PostgreSQL database."""

    with engine.connect() as connection:
        result = connection.execute(
            text("SELECT current_database(), current_user")
        )

        print("Database connection successful:", result.fetchone())


# ---------------------------------------------------------
# 4. CUSTOMER DATA GENERATION
# ---------------------------------------------------------

def generate_customers(count: int = 100) -> list[dict]:
    """Generate fictional Indian customer records."""

    customers = []

    for _ in range(count):
        customer = {
            "customer_id": uuid.uuid4(),
            "first_name": fake.first_name(),
            "last_name": fake.last_name(),
            "email": fake.unique.email(),
            "phone": fake.unique.msisdn()[-10:],
            "date_of_birth": fake.date_of_birth(
                minimum_age=21,
                maximum_age=65,
            ),
            "kyc_status": random.choices(
                ["VERIFIED", "PENDING", "REJECTED"],
                weights=[85, 10, 5],
            )[0],
            "customer_status": random.choices(
                ["ACTIVE", "INACTIVE", "BLOCKED"],
                weights=[90, 7, 3],
            )[0],
        }

        customers.append(customer)

    return customers


# ---------------------------------------------------------
# 5. ACCOUNT DATA GENERATION
# ---------------------------------------------------------

def generate_accounts(
        customers: list[dict],
) -> list[dict]:
    """Generate one or more accounts for each customer."""

    accounts = []

    account_types = ["SAVINGS", "CURRENT", "SALARY"]

    for customer in customers:
        # Each customer gets 1 or 2 accounts.
        number_of_accounts = random.choices(
            [1, 2],
            weights=[75, 25],
        )[0]

        for _ in range(number_of_accounts):
            account = {
                "account_id": uuid.uuid4(),
                "customer_id": customer["customer_id"],
                "account_number": fake.unique.bothify(
                    text="##########"
                ),
                "account_type": random.choices(
                    account_types,
                    weights=[75, 10, 15],
                )[0],
                "balance": Decimal(
                    str(random.randint(500, 500000))
                ).quantize(Decimal("0.01")),
                "currency": "INR",
                "account_status": random.choices(
                    ["ACTIVE", "FROZEN", "CLOSED"],
                    weights=[90, 7, 3],
                )[0],
            }

            accounts.append(account)

    return accounts

# ---------------------------------------------------------
# 7. CARD DATA GENERATION
# ---------------------------------------------------------

def generate_cards(
        customers: list[dict],
) -> list[dict]:
    """Generate fictional debit and credit cards."""

    cards = []

    for customer in customers:
        # Approximately 70% of customers receive a card.
        if random.random() > 0.70:
            continue

        number_of_cards = random.choices(
            [1, 2],
            weights=[85, 15],
        )[0]

        for _ in range(number_of_cards):
            expiry_date = fake.date_between(
                start_date="+1y",
                end_date="+5y",
            )

            card = {
                "card_id": uuid.uuid4(),
                "customer_id": customer["customer_id"],
                "card_last_four": str(
                    random.randint(1000, 9999)
                ),
                "card_type": random.choice(
                    ["DEBIT", "CREDIT"]
                ),
                "card_network": random.choice(
                    ["VISA", "MASTERCARD", "RUPAY"]
                ),
                "expiry_month": expiry_date.month,
                "expiry_year": expiry_date.year,
                "card_status": random.choices(
                    ["ACTIVE", "BLOCKED", "EXPIRED"],
                    weights=[90, 7, 3],
                )[0],
            }

            cards.append(card)

    return cards

def generate_transactions(
        accounts: list[dict],
        count: int = 500,
) -> list[dict]:
    """Generate fictional banking transactions."""
    transactions = []

    failure_scenarios = {
        "INSUFFICIENT_FUNDS": "Insufficient account balance",
        "INVALID_BENEFICIARY": "Beneficiary details are invalid",
        "DAILY_LIMIT_EXCEEDED": "Daily transaction limit exceeded",
        "ACCOUNT_FROZEN": "Account is frozen",
        "GATEWAY_TIMEOUT": "Payment gateway timed out",
        "ISSUER_UNAVAILABLE": "Issuer bank is unavailable",
    }

    for _ in range(count):
        transaction_status = random.choices(
            ["SUCCESS", "FAILED", "PENDING", "REVERSED"],
            weights=[75, 15, 7, 3],
        )[0]

        failure_code = None
        failure_reason = None

        if transaction_status == "FAILED":
            failure_code = random.choice(list(failure_scenarios.keys()))
            failure_reason = failure_scenarios[failure_code]

        transaction_timestamp = fake.date_time_between(
            start_date="-90d",
            end_date="now",
            tzinfo=UTC,
        )

        transaction = {
            "transaction_id": uuid.uuid4(),
            "account_id": random.choice(accounts)["account_id"],
            "transaction_reference": f"TXN{uuid.uuid4().hex[:16].upper()}",
            "amount": Decimal(
                str(random.randint(100, 100000))
            ).quantize(Decimal("0.01")),
            "currency": "INR",
            "transaction_type": random.choice(["DEBIT", "CREDIT"]),
            "payment_channel": random.choice(
                ["UPI", "CARD", "NEFT", "IMPS", "RTGS", "ATM", "INTERNAL"]
            ),
            "transaction_status": transaction_status,
            "failure_code": failure_code,
            "failure_reason": failure_reason,
            "merchant_name": fake.company(),
            "counterparty_reference": f"REF{uuid.uuid4().hex[:12].upper()}",
            "transaction_timestamp": transaction_timestamp,
        }

        transactions.append(transaction)

    return transactions


def validate_generated_data(
        customers: list[dict],
        accounts: list[dict],
        cards: list[dict],
        transactions: list[dict],
) -> None:
    """Validate relationships and constraints in generated data."""

    customer_ids = {customer["customer_id"] for customer in customers}
    account_ids = {account["account_id"] for account in accounts}

    # Validate account-to-customer relationships.
    assert all(
        account["customer_id"] in customer_ids
        for account in accounts
    ), "An account references a non-existent customer."

    # Validate card-to-customer relationships.
    assert all(
        card["customer_id"] in customer_ids
        for card in cards
    ), "A card references a non-existent customer."

    # Validate transaction-to-account relationships.
    assert all(
        transaction["account_id"] in account_ids
        for transaction in transactions
    ), "A transaction references a non-existent account."

    # Validate transaction reference uniqueness.
    transaction_references = [
        transaction["transaction_reference"]
        for transaction in transactions
    ]
    assert len(transaction_references) == len(set(transaction_references)), (
        "Duplicate transaction references found."
    )

    # Validate failure details.
    assert all(
        transaction["failure_code"] is not None
        and transaction["failure_reason"] is not None
        for transaction in transactions
        if transaction["transaction_status"] == "FAILED"
    ), "A failed transaction is missing failure details."

    assert all(
        transaction["failure_code"] is None
        and transaction["failure_reason"] is None
        for transaction in transactions
        if transaction["transaction_status"] != "FAILED"
    ), "A non-failed transaction contains failure details."

    print("\nData validation successful!")


def insert_generated_data(
        customers: list[dict],
        accounts: list[dict],
        cards: list[dict],
        transactions: list[dict],
) -> None:
    """Insert generated records into PostgreSQL."""

    insert_statements = {
        "customers": text("""
            INSERT INTO customers (
                customer_id, first_name, last_name, email, phone,
                date_of_birth, kyc_status, customer_status
            )
            VALUES (
                :customer_id, :first_name, :last_name, :email, :phone,
                :date_of_birth, :kyc_status, :customer_status
            )
        """),

        "accounts": text("""
            INSERT INTO accounts (
                account_id, customer_id, account_number, account_type,
                balance, currency, account_status
            )
            VALUES (
                :account_id, :customer_id, :account_number, :account_type,
                :balance, :currency, :account_status
            )
        """),

        "cards": text("""
            INSERT INTO cards (
                card_id, customer_id, card_last_four, card_type,
                card_network, expiry_month, expiry_year, card_status
            )
            VALUES (
                :card_id, :customer_id, :card_last_four, :card_type,
                :card_network, :expiry_month, :expiry_year, :card_status
            )
        """),

        "transactions": text("""
            INSERT INTO transactions (
                transaction_id, account_id, transaction_reference,
                amount, currency, transaction_type, payment_channel,
                transaction_status, failure_code, failure_reason,
                merchant_name, counterparty_reference,
                transaction_timestamp
            )
            VALUES (
                :transaction_id, :account_id, :transaction_reference,
                :amount, :currency, :transaction_type, :payment_channel,
                :transaction_status, :failure_code, :failure_reason,
                :merchant_name, :counterparty_reference,
                :transaction_timestamp
            )
        """),
    }

    # engine.begin() automatically commits on success and rolls back on error.
    with engine.begin() as connection:
        connection.execute(insert_statements["customers"], customers)
        connection.execute(insert_statements["accounts"], accounts)
        connection.execute(insert_statements["cards"], cards)
        connection.execute(insert_statements["transactions"], transactions)

    print("\nAll generated records inserted successfully!")


if __name__ == "__main__":
    customers = generate_customers(100)
    accounts = generate_accounts(customers)
    cards = generate_cards(customers)
    transactions = generate_transactions(accounts, 500)
    validate_generated_data(
        customers,
        accounts,
        cards,
        transactions,
    )
    insert_generated_data(
        customers,
        accounts,
        cards,
        transactions,
    )
    print(f"Customers generated: {len(customers)}")
    print(f"Accounts generated: {len(accounts)}")
    print(f"Cards generated: {len(cards)}")
    print(f"Transactions generated: {len(transactions)}")

    print("\nSample transaction:")
    print(transactions[0])