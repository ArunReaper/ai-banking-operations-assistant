# Synthetic SOP: Insufficient Funds Investigation

Document ID: SOP-BAL-001
Version: 1.0
Document Type: Demonstration Investigation Guide
Effective Date: 2026-11-01

IMPORTANT: This is a synthetic policy document created for an educational
portfolio project. It does not represent an actual bank policy.

## 1. Purpose

This guide describes how operations staff should investigate
transactions recorded with an insufficient-funds failure code.

## 2. Required Checks

Before concluding that insufficient funds caused a transaction
failure, verify:

- The transaction reference.
- The transaction amount and currency.
- The transaction type: DEBIT or CREDIT.
- The account associated with the transaction.
- The available balance at the time of transaction processing,
  where historical information is available.
- The recorded failure code and processing response.

## 3. Important Data Limitations

The current account balance may differ from the balance at the
time a transaction was processed.

A current balance alone cannot establish whether sufficient funds
were available at the historical transaction time.

If historical balance information is unavailable, explain this
limitation rather than claiming that insufficient funds have
been conclusively established.

## 4. Transaction Direction Validation

An insufficient-funds failure is generally associated with an
attempt to debit an account.

If the transaction is recorded as CREDIT:
- Do not automatically attribute the failure to the receiving
  customer's account balance.
- Investigate the transaction processing flow and source of the
  recorded failure code.
- Flag any mismatch between transaction direction and failure
  explanation for further investigation.

## 5. Escalation Criteria

Escalate the case when:
- The transaction type conflicts with the recorded failure code.
- Historical balance information is unavailable.
- The transaction record conflicts with account information.
- The failure code does not provide enough evidence to establish
  the actual cause.

## 6. Communication Guidelines

Distinguish between:
- Verified facts from transaction and account records.
- Possible explanations based on the recorded failure code.
- Information that remains unavailable or unverified.

Never present an unverified explanation as a confirmed root cause.
