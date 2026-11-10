# Synthetic SOP: IMPS Transaction Failure Handling

Document ID: SOP-IMPS-001
Version: 1.0
Document Type: Demonstration Standard Operating Procedure
Effective Date: 2026-11-01

IMPORTANT: This is a synthetic policy document created for an educational
portfolio project. It does not represent an actual bank policy.

## 1. Purpose

This document describes the investigation process for failed IMPS
transactions in a simulated banking operations environment.

## 2. Common Failure Scenarios

### 2.1 Gateway Timeout

A gateway timeout occurs when the payment gateway does not receive
a response from the downstream processing system within the expected
time window.

Recommended investigation:
- Check the transaction reference and timestamp.
- Review the gateway response and processing logs.
- Check whether the transaction is still pending.
- Verify the final transaction status before communicating an outcome.

Do not assume that a timeout means the transaction has permanently failed.
The final status must be verified.

### 2.2 Issuer Unavailable

This scenario occurs when the issuer or downstream banking system
is temporarily unavailable.

Recommended investigation:
- Verify the transaction status.
- Check the recorded failure response.
- Review whether the issue is isolated or part of a wider service disruption.
- Escalate recurring failures to the relevant technical operations team.

### 2.3 Invalid Beneficiary

This scenario indicates that the beneficiary information could not
be validated by the receiving system.

Recommended investigation:
- Verify the beneficiary details recorded against the transaction.
- Review the response code returned by the receiving system.
- Do not assume that the beneficiary account exists or is active.

## 3. Transaction Status Verification

Before providing an explanation, verify the transaction's latest
recorded status.

Possible statuses in this demonstration system:

- SUCCESS: The transaction is recorded as successful.
- FAILED: The transaction is recorded as failed.
- PENDING: The final outcome has not yet been established.
- REVERSED: The transaction has been recorded as reversed.

A failure response and a transaction's final status should not
be treated as interchangeable.

## 4. Escalation

Escalate a transaction when:
- Its status remains unresolved.
- The recorded response conflicts with other transaction information.
- Multiple transactions show similar failures.
- The available information is insufficient to explain the outcome.

## 5. Customer Communication

Communication must be based on verified transaction information.
Never confirm a refund, reversal, or successful settlement unless
the relevant status is explicitly verified.

## 6. Refund and Reversal Confirmation

- A PENDING transaction must not be communicated as refunded.
- Verify the latest transaction status before confirming a refund or reversal.
- A transaction marked REVERSED may be described as reversed
  according to the recorded transaction status.
- A transaction marked FAILED must not automatically be
  described as refunded.
- If the final status is unavailable, communicate that the
  outcome remains unconfirmed and escalate where required.