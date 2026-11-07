-- =========================================================
-- AI Banking Operations Assistant
-- Database: banking_ops
-- Currency: INR
-- Synthetic banking data only
-- =========================================================

-- 1. CUSTOMERS
CREATE TABLE IF NOT EXISTS customers (
    customer_id UUID PRIMARY KEY,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    email VARCHAR(255) UNIQUE,
    phone VARCHAR(20) UNIQUE,
    date_of_birth DATE,
    kyc_status VARCHAR(20) NOT NULL DEFAULT 'PENDING'
        CHECK (kyc_status IN ('PENDING', 'VERIFIED', 'REJECTED')),
    customer_status VARCHAR(20) NOT NULL DEFAULT 'ACTIVE'
        CHECK (customer_status IN ('ACTIVE', 'INACTIVE', 'BLOCKED')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);


-- 2. ACCOUNTS
CREATE TABLE IF NOT EXISTS accounts (
    account_id UUID PRIMARY KEY,
    customer_id UUID NOT NULL REFERENCES customers(customer_id),
    account_number VARCHAR(20) NOT NULL UNIQUE,
    account_type VARCHAR(20) NOT NULL
        CHECK (account_type IN ('SAVINGS', 'CURRENT', 'SALARY')),
    balance NUMERIC(18, 2) NOT NULL DEFAULT 0.00
        CHECK (balance >= 0),
    currency CHAR(3) NOT NULL DEFAULT 'INR'
        CHECK (currency = 'INR'),
    account_status VARCHAR(20) NOT NULL DEFAULT 'ACTIVE'
        CHECK (account_status IN ('ACTIVE', 'FROZEN', 'CLOSED')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);


-- 3. TRANSACTIONS
CREATE TABLE IF NOT EXISTS transactions (
    transaction_id UUID PRIMARY KEY,
    account_id UUID NOT NULL REFERENCES accounts(account_id),
    transaction_reference VARCHAR(50) NOT NULL UNIQUE,
    amount NUMERIC(18, 2) NOT NULL CHECK (amount > 0),
    currency CHAR(3) NOT NULL DEFAULT 'INR'
        CHECK (currency = 'INR'),
    transaction_type VARCHAR(20) NOT NULL
        CHECK (transaction_type IN ('DEBIT', 'CREDIT')),
    payment_channel VARCHAR(20) NOT NULL
        CHECK (
            payment_channel IN (
                'UPI', 'CARD', 'NEFT', 'IMPS',
                'RTGS', 'ATM', 'INTERNAL'
            )
        ),
    transaction_status VARCHAR(20) NOT NULL
        CHECK (
            transaction_status IN (
                'SUCCESS', 'FAILED', 'PENDING', 'REVERSED'
            )
        ),
    failure_code VARCHAR(30),
    failure_reason TEXT,
    merchant_name VARCHAR(255),
    counterparty_reference VARCHAR(100),
    transaction_timestamp TIMESTAMPTZ NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);


-- 4. CARDS
CREATE TABLE IF NOT EXISTS cards (
    card_id UUID PRIMARY KEY,
    customer_id UUID NOT NULL REFERENCES customers(customer_id),
    card_last_four CHAR(4) NOT NULL,
    card_type VARCHAR(20) NOT NULL
        CHECK (card_type IN ('DEBIT', 'CREDIT')),
    card_network VARCHAR(20) NOT NULL
        CHECK (card_network IN ('VISA', 'MASTERCARD', 'RUPAY')),
    expiry_month SMALLINT NOT NULL
        CHECK (expiry_month BETWEEN 1 AND 12),
    expiry_year SMALLINT NOT NULL,
    card_status VARCHAR(20) NOT NULL DEFAULT 'ACTIVE'
        CHECK (card_status IN ('ACTIVE', 'BLOCKED', 'EXPIRED')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);


-- 5. INDEXES FOR COMMON INVESTIGATION QUERIES

CREATE INDEX IF NOT EXISTS idx_accounts_customer_id
    ON accounts(customer_id);

CREATE INDEX IF NOT EXISTS idx_transactions_account_id
    ON transactions(account_id);

CREATE INDEX IF NOT EXISTS idx_transactions_timestamp
    ON transactions(transaction_timestamp DESC);

CREATE INDEX IF NOT EXISTS idx_transactions_status
    ON transactions(transaction_status);

CREATE INDEX IF NOT EXISTS idx_transactions_reference
    ON transactions(transaction_reference);

CREATE INDEX IF NOT EXISTS idx_cards_customer_id
    ON cards(customer_id);
