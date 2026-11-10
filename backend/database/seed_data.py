import argparse
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



FAILURE_SCENARIOS = {
    "INSUFFICIENT_FUNDS": "Insufficient account balance",
    "INVALID_BENEFICIARY": "Beneficiary details are invalid",
    "DAILY_LIMIT_EXCEEDED": "Daily transaction limit exceeded",
    "ACCOUNT_FROZEN": "Account is frozen",
    "GATEWAY_TIMEOUT": "Payment gateway timed out",
    "ISSUER_UNAVAILABLE": "Issuer bank is unavailable",
}

FAILURE_RULES = {
    "INSUFFICIENT_FUNDS": {
        "transaction_type": "DEBIT",
        "channels": ["UPI", "CARD", "NEFT", "IMPS", "RTGS", "ATM", "INTERNAL"],
        "account_status": "ACTIVE",
    },
    "INVALID_BENEFICIARY": {
        "transaction_type": "DEBIT",
        "channels": ["UPI", "NEFT", "IMPS", "RTGS"],
        "account_status": "ACTIVE",
    },
    "DAILY_LIMIT_EXCEEDED": {
        "transaction_type": "DEBIT",
        "channels": ["UPI", "CARD", "NEFT", "IMPS", "RTGS", "ATM"],
        "account_status": "ACTIVE",
    },
    "ACCOUNT_FROZEN": {
        "transaction_type": "DEBIT",
        "channels": ["UPI", "CARD", "NEFT", "IMPS", "RTGS", "ATM", "INTERNAL"],
        "account_status": "FROZEN",
    },
    "GATEWAY_TIMEOUT": {
        "transaction_type": "DEBIT",
        "channels": ["UPI", "CARD", "NEFT", "IMPS", "RTGS"],
        "account_status": "ACTIVE",
    },
    "ISSUER_UNAVAILABLE": {
        "transaction_type": "DEBIT",
        "channels": ["UPI", "CARD"],
        "account_status": "ACTIVE",
    },
}

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
    """Generate fictional banking transactions with consistent failure scenarios."""

    if not accounts:
        raise ValueError("At least one account is required.")

    active_accounts = [
        account for account in accounts
        if account["account_status"] == "ACTIVE"
    ]
    frozen_accounts = [
        account for account in accounts
        if account["account_status"] == "FROZEN"
    ]

    if not active_accounts:
        raise ValueError("At least one ACTIVE account is required.")

    available_failure_codes = [
        code
        for code, rules in FAILURE_RULES.items()
        if (
                rules["account_status"] == "ACTIVE"
                or frozen_accounts
        )
    ]

    transactions = []

    for _ in range(count):
        transaction_status = random.choices(
            ["SUCCESS", "FAILED", "PENDING", "REVERSED"],
            weights=[75, 15, 7, 3],
        )[0]

        failure_code = None
        failure_reason = None

        if transaction_status == "FAILED":
            failure_code = random.choice(available_failure_codes)
            failure_reason = FAILURE_SCENARIOS[failure_code]

            rules = FAILURE_RULES[failure_code]

            transaction_type = rules["transaction_type"]
            payment_channel = random.choice(rules["channels"])

            if rules["account_status"] == "FROZEN":
                account = random.choice(frozen_accounts)
            else:
                account = random.choice(active_accounts)

        else:
            # Non-failed transactions use active accounts in this model.
            account = random.choice(active_accounts)
            transaction_type = random.choice(["DEBIT", "CREDIT"])
            payment_channel = random.choice(
                ["UPI", "CARD", "NEFT", "IMPS", "RTGS", "ATM", "INTERNAL"]
            )

        transaction_timestamp = fake.date_time_between(
            start_date="-90d",
            end_date="now",
            tzinfo=UTC,
        )

        transaction = {
            "transaction_id": uuid.uuid4(),
            "account_id": account["account_id"],
            "transaction_reference": f"TXN{uuid.uuid4().hex[:16].upper()}",
            "amount": Decimal(
                str(random.randint(100, 100000))
            ).quantize(Decimal("0.01")),
            "currency": "INR",
            "transaction_type": transaction_type,
            "payment_channel": payment_channel,
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
    """Validate relationships and consistency in generated banking data."""

    customer_ids = {customer["customer_id"] for customer in customers}
    accounts_by_id = {
        account["account_id"]: account for account in accounts
    }

    # Validate account-to-customer relationships.
    if not all(
            account["customer_id"] in customer_ids
            for account in accounts
    ):
        raise ValueError("An account references a non-existent customer.")

    # Validate card-to-customer relationships.
    if not all(
            card["customer_id"] in customer_ids
            for card in cards
    ):
        raise ValueError("A card references a non-existent customer.")

    # Validate transaction-to-account relationships.
    if not all(
            transaction["account_id"] in accounts_by_id
            for transaction in transactions
    ):
        raise ValueError("A transaction references a non-existent account.")

    # Validate transaction reference uniqueness.
    transaction_references = [
        transaction["transaction_reference"]
        for transaction in transactions
    ]

    if len(transaction_references) != len(set(transaction_references)):
        raise ValueError("Duplicate transaction references found.")

    allowed_statuses = {"SUCCESS", "FAILED", "PENDING", "REVERSED"}

    for transaction in transactions:
        status = transaction["transaction_status"]
        failure_code = transaction["failure_code"]
        failure_reason = transaction["failure_reason"]

        account = accounts_by_id[transaction["account_id"]]
        account_status = account["account_status"]

        # Validate transaction status.
        if status not in allowed_statuses:
            raise ValueError(
                f"Invalid transaction status: {status}"
            )

        if status == "FAILED":
            # Failed transactions must contain failure details.
            if not failure_code or not failure_reason:
                raise ValueError(
                    "A failed transaction is missing failure details."
                )

            # Failure code must be recognised.
            if failure_code not in FAILURE_RULES:
                raise ValueError(
                    f"Unknown failure code: {failure_code}"
                )

            rules = FAILURE_RULES[failure_code]

            # Failure reason must match the configured scenario.
            if failure_reason != FAILURE_SCENARIOS[failure_code]:
                raise ValueError(
                    f"Incorrect failure reason for {failure_code}."
                )

            # Validate transaction type.
            if transaction["transaction_type"] != rules["transaction_type"]:
                raise ValueError(
                    f"{failure_code} has an incompatible transaction type."
                )

            # Validate payment channel.
            if transaction["payment_channel"] not in rules["channels"]:
                raise ValueError(
                    f"{failure_code} has an incompatible payment channel."
                )

            # Validate account status.
            if account_status != rules["account_status"]:
                raise ValueError(
                    f"{failure_code} references an account with "
                    f"status {account_status}; expected "
                    f"{rules['account_status']}."
                )

        else:
            # Non-failed transactions must not contain failure details.
            if failure_code is not None or failure_reason is not None:
                raise ValueError(
                    "A non-failed transaction contains failure details."
                )

            # Non-failed transactions must use active accounts
            # in this simplified synthetic dataset.
            if account_status != "ACTIVE":
                raise ValueError(
                    "A non-failed transaction references a "
                    f"{account_status} account."
                )

    print("\nData validation successful!")



def insert_generated_data(
        customers: list[dict],
        accounts: list[dict],
        cards: list[dict],
        transactions: list[dict],
        reset: bool = False,
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

    # Keep deletion and insertion in one transaction.
    # If any operation fails, the entire transaction is rolled back.
    with engine.begin() as connection:
        if reset:
            delete_statements = [
                "DELETE FROM transactions",
                "DELETE FROM cards",
                "DELETE FROM accounts",
                "DELETE FROM customers",
            ]

            for statement in delete_statements:
                connection.execute(text(statement))

        connection.execute(insert_statements["customers"], customers)
        connection.execute(insert_statements["accounts"], accounts)
        connection.execute(insert_statements["cards"], cards)
        connection.execute(insert_statements["transactions"], transactions)

    print("\nAll generated records inserted successfully!")

def is_database_empty() -> bool:
    """Check whether the banking tables contain any records."""

    tables = ["customers", "accounts", "cards", "transactions"]

    with engine.connect() as connection:
        for table in tables:
            result = connection.execute(
                text(f"SELECT EXISTS (SELECT 1 FROM {table})")
            ).scalar()

            if result:
                return False

    return True


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Generate synthetic banking data."
    )
    parser.add_argument(
        "--reset",
        action="store_true",
        help="Replace existing records with a new synthetic dataset.",
    )
    args = parser.parse_args()

    # Step 1: Generate the complete dataset in memory.
    customers = generate_customers(100)
    accounts = generate_accounts(customers)
    cards = generate_cards(customers)
    transactions = generate_transactions(accounts, 500)

    # Step 2: Validate everything before touching the database.
    validate_generated_data(
        customers,
        accounts,
        cards,
        transactions,
    )

    # Step 3: Check whether replacement is permitted.
    if args.reset:
        confirmation = input(
            "WARNING: This will replace all existing records "
            "in customers, accounts, cards and transactions. "
            "Continue? (yes/no): "
        )

        if confirmation.strip().lower() != "yes":
            print("Operation cancelled. Existing data was not changed.")
            raise SystemExit(0)

    elif not is_database_empty():
        print(
            "Database already contains records. "
            "Use --reset to replace the synthetic dataset."
        )
        raise SystemExit(1)

    # Step 4: Insert the dataset, optionally replacing existing records.
    insert_generated_data(
        customers,
        accounts,
        cards,
        transactions,
        reset=args.reset,
    )

    print("\n--- Dataset Generation Summary ---")
    print(f"Customers generated: {len(customers)}")
    print(f"Accounts generated: {len(accounts)}")
    print(f"Cards generated: {len(cards)}")
    print(f"Transactions generated: {len(transactions)}")
