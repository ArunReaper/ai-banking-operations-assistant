
from unittest.mock import Mock

import pytest
import requests
from backend.services.llm_service import (
    LLMProviderError,
    generate_response,
)


def test_generate_response_success(monkeypatch):
    """Test successful response from OpenRouter."""

    monkeypatch.setenv("OPENROUTER_API_KEY", "test-api-key")
    monkeypatch.setenv(
        "OPENROUTER_MODEL",
        "nvidia/nemotron-3.5-lightning:free",
    )

    mock_response = Mock()
    mock_response.json.return_value = {
        "choices": [
            {
                "message": {
                    "content": "There are three r's in strawberry."
                }
            }
        ]
    }
    mock_response.raise_for_status.return_value = None

    mock_post = Mock(return_value=mock_response)
    monkeypatch.setattr(
        "backend.services.llm_service.requests.post",
        mock_post,
    )

    result = generate_response("How many r's are in strawberry?")

    assert result == "There are three r's in strawberry."

    # Verify that the request uses the configured model.
    request_payload = mock_post.call_args.kwargs["json"]
    assert request_payload["model"] == "nvidia/nemotron-3.5-lightning:free"


def test_generate_response_empty_prompt():
    """Test that an empty prompt is rejected."""

    with pytest.raises(ValueError, match="Prompt cannot be empty"):
        generate_response("")


def test_generate_response_missing_api_key(monkeypatch):
    """Test that a missing API key raises an error."""

    monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)

    with pytest.raises(LLMProviderError, match="OPENROUTER_API_KEY"):
        generate_response("Test prompt")


def test_generate_response_http_error(monkeypatch):
    """Test handling of HTTP errors."""

    monkeypatch.setenv("OPENROUTER_API_KEY", "test-api-key")

    mock_post = Mock()
    mock_post.return_value.raise_for_status.side_effect = (
        requests.exceptions.HTTPError("429 Too Many Requests")
    )

    monkeypatch.setattr(
        "backend.services.llm_service.requests.post",
        mock_post,
    )

    with pytest.raises(
            LLMProviderError,
            match="Unable to communicate",
    ):
        generate_response("Test prompt")


def test_generate_response_invalid_response(monkeypatch):
    """Test handling of an unexpected response structure."""

    monkeypatch.setenv("OPENROUTER_API_KEY", "test-api-key")

    mock_response = Mock()
    mock_response.json.return_value = {"unexpected": "response"}
    mock_response.raise_for_status.return_value = None

    monkeypatch.setattr(
        "backend.services.llm_service.requests.post",
        Mock(return_value=mock_response),
    )

    with pytest.raises(LLMProviderError, match="Invalid response"):
        generate_response("Test prompt")
