
import logging
import os
import time

import requests

logger = logging.getLogger(__name__)

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"


class LLMProviderError(Exception):
    """Raised when the configured LLM provider request fails."""


def generate_response(
        prompt: str,
        temperature: float = 0.2,
        max_output_tokens: int = 1500,
) -> str:
    """Generate a response using the configured OpenRouter model."""

    if not prompt or not prompt.strip():
        raise ValueError("Prompt cannot be empty.")

    if not 0.0 <= temperature <= 2.0:
        raise ValueError("Temperature must be between 0 and 2.")

    if max_output_tokens <= 0:
        raise ValueError("Maximum output tokens must be positive.")

    api_key = os.getenv("OPENROUTER_API_KEY")
    model = os.getenv(
        "OPENROUTER_MODEL",
        "nvidia/nemotron-3.5-lightning:free",
    )

    if not api_key:
        raise LLMProviderError("OPENROUTER_API_KEY is not configured.")

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": model,
        "messages": [
            {"role": "user", "content": prompt},
        ],
        "temperature": temperature,
        "max_tokens": max_output_tokens,
        "reasoning": {
            "enabled": False,
        },
    }

    start_time = time.perf_counter()

    try:
        response = requests.post(
            OPENROUTER_URL,
            headers=headers,
            json=payload,
            timeout=60,
        )

        response.raise_for_status()
        result = response.json()

        content = result["choices"][0]["message"]["content"]

        finish_reason = result["choices"][0].get("finish_reason")

        if finish_reason == "length":
            raise LLMProviderError(
                "The model response was truncated because the token limit was reached."
            )

        if not isinstance(content, str) or not content.strip():
            raise LLMProviderError("The LLM provider returned an empty response.")

        elapsed_time = time.perf_counter() - start_time

        logger.info(
            "OpenRouter request completed using model %s in %.2f seconds",
            model,
            elapsed_time,
        )

        return content.strip()

    except requests.exceptions.Timeout as error:
        raise LLMProviderError("The LLM provider request timed out.") from error

    except requests.exceptions.RequestException as error:
        logger.error("OpenRouter HTTP request failed: %s", type(error).__name__)
        raise LLMProviderError("Unable to communicate with the LLM provider.") from error

    except (KeyError, IndexError, TypeError, ValueError) as error:
        if isinstance(error, LLMProviderError):
            raise
        raise LLMProviderError("Invalid response received from the LLM provider.") from error
