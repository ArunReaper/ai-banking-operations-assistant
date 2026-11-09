
import os

import requests

API_BASE_URL = os.getenv(
    "BANKING_API_URL",
    "http://127.0.0.1:8000",
)


def get_transaction_details(transaction_reference: str) -> dict:
    """Retrieve transaction details from the FastAPI backend."""

    url = (
        f"{API_BASE_URL}/api/v1/transactions/"
        f"{transaction_reference}"
    )

    response = requests.get(url, timeout=10)

    if response.status_code == 404:
        raise ValueError("Transaction not found.")

    response.raise_for_status()

    return response.json()

def ask_assistant(message: str) -> str:
    """Send a natural-language question to the AI assistant."""

    url = f"{API_BASE_URL}/api/v1/assistant/ask"

    response = requests.post(
        url,
        json={"message": message},
        timeout=60,
    )

    response.raise_for_status()

    return response.json()["answer"]