# Synthetic SOP: UPI Transaction Failure Handling

Document ID: SOP-UPI-001
Version: 1.0
Document Type: Demonstration Standard Operating Procedure
Effective Date: 2026-11-01

IMPORTANT: This is a synthetic policy document created for an educational
portfolio project. It does not represent an actual bank policy.

## 1. Purpose

This document describes the investigation process for failed UPI
transactions in a simulated banking operations environment.

## 2. Common Failure Scenarios

### 2.1 Insufficient Funds

This scenario indicates that the transaction could not be processed
because the available balance in the relevant debit account was
insufficient.

Recommended investigation:
- Verify the transaction type and direction.
- Check the account associated with the debit transaction.
- Compare the transaction amount with the available balance at the
  time of processing, if historical balance information is available.
- Do not use the current account balance as proof of the historical
  balance at transaction time.

### 2.2 Daily Transaction Limit Exceeded

This scenario indicates that a transaction could not be processed
because an applicable transaction limit was reached.

Recommended investigation:
- Verify the recorded failure response.
- Review the transaction amount and relevant transaction history.
- Check the applicable limit configuration, if available.
- Do not assume a specific limit without verified configuration data.

### 2.3 Account Frozen

This scenario indicates that the account was restricted from
performing the requested transaction.

Recommended investigation:
- Verify the account status recorded by the banking system.
- Check whether the restriction was active at transaction time.
- Escalate discrepancies between account status and transaction
  failure information.

## 3. Transaction Direction

Transaction direction is important when investigating insufficient
funds.

- DEBIT: Funds are expected to leave the account.
- CREDIT: Funds are expected to enter the account.

An insufficient-funds explanation should not automatically be
applied to an incoming credit transaction without additional
evidence about the actual processing flow.

## 4. Transaction Status

Always verify the latest recorded transaction status before
communicating the outcome.

A failed transaction should not automatically be described as
refunded or reversed.

## 5. Customer Communication

Provide explanations using verified transaction and account data.
If historical balance or limit information is unavailable, clearly
state that the cause cannot be independently confirmed.
