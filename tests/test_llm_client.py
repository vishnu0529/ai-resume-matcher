from unittest.mock import MagicMock, patch

from app.core.config import settings
from app.services.llm_client import call_llm


def _mock_anthropic_response():
    response = MagicMock()
    response.content = [MagicMock(text="answer")]
    return response


def test_anthropic_short_system_prompt_is_not_cached():
    mock_client = MagicMock()
    mock_client.messages.create.return_value = _mock_anthropic_response()

    with (
        patch.object(settings, "LLM_PROVIDER", "anthropic"),
        patch("anthropic.Anthropic", return_value=mock_client),
    ):
        call_llm("short system prompt", "question")

    kwargs = mock_client.messages.create.call_args.kwargs
    assert kwargs["system"] == "short system prompt"


def test_anthropic_long_system_prompt_gets_cache_control():
    mock_client = MagicMock()
    mock_client.messages.create.return_value = _mock_anthropic_response()
    long_prompt = "x" * 4096

    with (
        patch.object(settings, "LLM_PROVIDER", "anthropic"),
        patch("anthropic.Anthropic", return_value=mock_client),
    ):
        call_llm(long_prompt, "question")

    kwargs = mock_client.messages.create.call_args.kwargs
    assert kwargs["system"] == [
        {"type": "text", "text": long_prompt, "cache_control": {"type": "ephemeral"}}
    ]
