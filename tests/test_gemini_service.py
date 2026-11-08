
from types import SimpleNamespace

import pytest
from backend.services import gemini_service


def test_generate_response_success(monkeypatch):
    """Verify that the Gemini service returns the generated text."""

    mock_response = SimpleNamespace(
        text="The UPI transaction failed."
    )

    mock_client = SimpleNamespace(
        models=SimpleNamespace(
            generate_content=lambda **kwargs: mock_response
        )
    )

    monkeypatch.setattr(
        gemini_service,
        "get_gemini_client",
        lambda: mock_client,
    )
    monkeypatch.setattr(
        gemini_service,
        "get_gemini_model",
        lambda: "gemini-3.8-flash",
    )

    result = gemini_service.generate_response(
        "Explain a failed UPI transaction."
    )

    assert result == "The UPI transaction failed."


def test_generate_response_empty_prompt():
    """Verify that an empty prompt is rejected."""

    with pytest.raises(ValueError, match="Prompt cannot be empty"):
        gemini_service.generate_response("   ")


def test_generate_response_invalid_temperature():
    """Verify that an invalid temperature is rejected."""

    with pytest.raises(ValueError, match="Temperature must be between"):
        gemini_service.generate_response(
            "Explain a failed transaction.",
            temperature=3,
        )


def test_generate_response_invalid_max_output_tokens():
    """Verify that an invalid token limit is rejected."""

    with pytest.raises(ValueError, match="max_output_tokens must be at least 1"):
        gemini_service.generate_response(
            "Explain a failed transaction.",
            max_output_tokens=0,
        )


def test_generate_response_without_text(monkeypatch):
    """Verify that an empty Gemini response is handled."""

    mock_response = SimpleNamespace(text=None)

    mock_client = SimpleNamespace(
        models=SimpleNamespace(
            generate_content=lambda **kwargs: mock_response
        )
    )

    monkeypatch.setattr(
        gemini_service,
        "get_gemini_client",
        lambda: mock_client,
    )

    with pytest.raises(RuntimeError, match="Gemini returned no text"):
        gemini_service.generate_response(
            "Explain a failed transaction."
        )
