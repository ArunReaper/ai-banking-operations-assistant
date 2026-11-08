
import os
from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv
from google import genai
from google.genai import types

PROJECT_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(PROJECT_ROOT / ".env")


@lru_cache(maxsize=1)
def get_gemini_client() -> genai.Client:
    """Create and return a reusable Gemini client."""
    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key or api_key == "your-gemini-api-key-here":
        raise RuntimeError(
            "GEMINI_API_KEY is missing. "
            "Configure it in the project-root .env file."
        )

    return genai.Client(api_key=api_key)


def get_gemini_model() -> str:
    """Return the configured Gemini model name."""
    return os.getenv("GEMINI_MODEL", "gemini-3.8-flash")


def generate_response(
        prompt: str,
        temperature: float = 0.2,
        max_output_tokens: int = 512,
) -> str:
    """Generate a text response using the configured Gemini model."""
    if not prompt.strip():
        raise ValueError("Prompt cannot be empty.")

    if not 0 <= temperature <= 2:
        raise ValueError("Temperature must be between 0 and 2.")

    if max_output_tokens < 1:
        raise ValueError("max_output_tokens must be at least 1.")

    client = get_gemini_client()

    response = client.models.generate_content(
        model=get_gemini_model(),
        contents=prompt,
        config=types.GenerateContentConfig(
            temperature=temperature,
            max_output_tokens=max_output_tokens,
        ),
    )

    if response.text is None:
        raise RuntimeError("Gemini returned no text response.")

    return response.text
