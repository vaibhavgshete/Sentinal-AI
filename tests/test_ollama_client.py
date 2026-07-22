from unittest.mock import Mock, patch

import requests

from sentinel_ai.ollama_client import ask_llm, is_successful_analysis


def test_is_successful_analysis_true_for_normal_response():
    assert is_successful_analysis("ROOT CAUSE: ...") is True


def test_is_successful_analysis_false_for_empty_response():
    assert is_successful_analysis("") is False


def test_is_successful_analysis_false_for_none():
    assert is_successful_analysis(None) is False


def test_is_successful_analysis_false_for_error_prefix():
    assert is_successful_analysis("[ERROR] Ollama not available") is False


@patch("sentinel_ai.ollama_client.requests.post")
def test_ask_llm_returns_stripped_model_response(mock_post):
    mock_response = Mock()
    mock_response.json.return_value = {"response": "  ROOT CAUSE: bad import  "}
    mock_response.raise_for_status.return_value = None
    mock_post.return_value = mock_response

    result = ask_llm("boom", model="gemma3:4b", api_url="http://localhost:11434/api/generate")

    assert result == "ROOT CAUSE: bad import"
    mock_post.assert_called_once()


@patch("sentinel_ai.ollama_client.requests.post", side_effect=requests.exceptions.ConnectionError())
def test_ask_llm_handles_connection_error(mock_post):
    result = ask_llm("boom", model="gemma3:4b", api_url="http://localhost:11434/api/generate")
    assert result == "[ERROR] Ollama not available. Make sure 'ollama serve' is running"


@patch("sentinel_ai.ollama_client.requests.post", side_effect=requests.exceptions.Timeout())
def test_ask_llm_handles_timeout(mock_post):
    result = ask_llm("boom", model="gemma3:4b", api_url="http://localhost:11434/api/generate")
    assert result == "[ERROR] Ollama request timed out"


@patch("sentinel_ai.ollama_client.requests.post", side_effect=ValueError("boom"))
def test_ask_llm_handles_unexpected_error(mock_post):
    result = ask_llm("boom", model="gemma3:4b", api_url="http://localhost:11434/api/generate")
    assert result == "[ERROR] Failed to query Ollama: boom"
