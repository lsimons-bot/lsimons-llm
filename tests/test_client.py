"""Tests for synchronous LLM client."""

from typing import Any
from unittest.mock import MagicMock, patch

import httpx
import pytest

from lsimons_llm.client import (
    LLMClient,
    _extract_content,  # pyright: ignore[reportPrivateUsage]
    chat,
)
from lsimons_llm.config import LLMConfig
from lsimons_llm.exceptions import LLMRequestError, LLMResponseError


@pytest.fixture
def config() -> LLMConfig:
    return LLMConfig(
        base_url="http://test-api",
        api_key="test-key",
        model="test-model",
        max_tokens=100,
        temperature=0.5,
        timeout=30,
        max_retries=2,
    )


@pytest.fixture
def mock_response() -> dict[str, Any]:
    return {
        "choices": [
            {
                "message": {
                    "role": "assistant",
                    "content": "Hello! How can I help?",
                }
            }
        ]
    }


class TestLLMClient:
    def test_chat_returns_content(self, config: LLMConfig, mock_response: dict[str, Any]) -> None:
        with patch.object(httpx.Client, "post") as mock_post:
            mock_resp = MagicMock()
            mock_resp.json.return_value = mock_response
            mock_resp.raise_for_status.return_value = None
            mock_post.return_value = mock_resp

            client = LLMClient(config)
            result = client.chat([{"role": "user", "content": "Hi"}])

            assert result == "Hello! How can I help?"

    def test_chat_raw_returns_full_response(
        self, config: LLMConfig, mock_response: dict[str, Any]
    ) -> None:
        with patch.object(httpx.Client, "post") as mock_post:
            mock_resp = MagicMock()
            mock_resp.json.return_value = mock_response
            mock_resp.raise_for_status.return_value = None
            mock_post.return_value = mock_resp

            client = LLMClient(config)
            result = client.chat_raw([{"role": "user", "content": "Hi"}])

            assert result == mock_response

    def test_chat_sends_correct_payload(self, config: LLMConfig) -> None:
        with patch.object(httpx.Client, "post") as mock_post:
            mock_resp = MagicMock()
            mock_resp.json.return_value = {"choices": [{"message": {"content": "ok"}}]}
            mock_resp.raise_for_status.return_value = None
            mock_post.return_value = mock_resp

            client = LLMClient(config)
            client.chat([{"role": "user", "content": "test"}])

            mock_post.assert_called_once()
            call_args = mock_post.call_args
            assert call_args[1]["json"]["model"] == "test-model"
            assert call_args[1]["json"]["messages"] == [{"role": "user", "content": "test"}]
            assert call_args[1]["json"]["max_tokens"] == 100
            assert call_args[1]["json"]["temperature"] == 0.5

    def test_chat_with_tools(self, config: LLMConfig) -> None:
        with patch.object(httpx.Client, "post") as mock_post:
            mock_resp = MagicMock()
            mock_resp.json.return_value = {"choices": [{"message": {"content": "ok"}}]}
            mock_resp.raise_for_status.return_value = None
            mock_post.return_value = mock_resp

            client = LLMClient(config)
            tools = [{"type": "function", "function": {"name": "test"}}]
            client.chat([{"role": "user", "content": "test"}], tools=tools)

            call_args = mock_post.call_args
            assert call_args[1]["json"]["tools"] == tools

    def test_chat_with_overrides(self, config: LLMConfig) -> None:
        with patch.object(httpx.Client, "post") as mock_post:
            mock_resp = MagicMock()
            mock_resp.json.return_value = {"choices": [{"message": {"content": "ok"}}]}
            mock_resp.raise_for_status.return_value = None
            mock_post.return_value = mock_resp

            client = LLMClient(config)
            client.chat(
                [{"role": "user", "content": "test"}],
                model="override-model",
                temperature=0.9,
                max_tokens=500,
            )

            call_args = mock_post.call_args
            assert call_args[1]["json"]["model"] == "override-model"
            assert call_args[1]["json"]["temperature"] == 0.9
            assert call_args[1]["json"]["max_tokens"] == 500

    def test_chat_retries_on_server_error(self, config: LLMConfig) -> None:
        with patch.object(httpx.Client, "post") as mock_post:
            error_resp = MagicMock()
            error_resp.status_code = 500
            error_resp.raise_for_status.side_effect = httpx.HTTPStatusError(
                "Server error", request=MagicMock(), response=error_resp
            )

            success_resp = MagicMock()
            success_resp.json.return_value = {"choices": [{"message": {"content": "ok"}}]}
            success_resp.raise_for_status.return_value = None

            mock_post.side_effect = [error_resp, success_resp]

            client = LLMClient(config)
            with patch("time.sleep"):
                result = client.chat([{"role": "user", "content": "test"}])

            assert result == "ok"
            assert mock_post.call_count == 2

    def test_chat_no_retry_on_client_error(self, config: LLMConfig) -> None:
        with patch.object(httpx.Client, "post") as mock_post:
            error_resp = MagicMock()
            error_resp.status_code = 400
            error_resp.raise_for_status.side_effect = httpx.HTTPStatusError(
                "Bad request", request=MagicMock(), response=error_resp
            )
            mock_post.return_value = error_resp

            client = LLMClient(config)
            with pytest.raises(LLMRequestError) as exc_info:
                client.chat([{"role": "user", "content": "test"}])

            assert exc_info.value.status_code == 400
            assert mock_post.call_count == 1

    def test_context_manager(self, config: LLMConfig) -> None:
        with patch.object(httpx.Client, "close") as mock_close:
            with LLMClient(config) as client:
                assert isinstance(client, LLMClient)
            mock_close.assert_called_once()


class TestExtractContent:
    def test_extracts_content(self) -> None:
        response = {"choices": [{"message": {"content": "test content"}}]}
        assert _extract_content(response) == "test content"

    def test_raises_on_no_choices(self) -> None:
        with pytest.raises(LLMResponseError, match="No choices"):
            _extract_content({"choices": []})

    def test_raises_on_no_content(self) -> None:
        with pytest.raises(LLMResponseError, match="No content"):
            _extract_content({"choices": [{"message": {}}]})


class TestLLMClientErrors:
    def test_chat_retries_on_network_error(self, config: LLMConfig) -> None:
        with patch.object(httpx.Client, "post") as mock_post:
            mock_post.side_effect = [
                httpx.RequestError("Connection failed"),
                MagicMock(
                    json=MagicMock(return_value={"choices": [{"message": {"content": "ok"}}]}),
                    raise_for_status=MagicMock(return_value=None),
                ),
            ]

            client = LLMClient(config)
            with patch("time.sleep"):
                result = client.chat([{"role": "user", "content": "test"}])

            assert result == "ok"
            assert mock_post.call_count == 2

    def test_chat_raises_after_all_retries_exhausted(self, config: LLMConfig) -> None:
        with patch.object(httpx.Client, "post") as mock_post:
            mock_post.side_effect = httpx.RequestError("Connection failed")

            client = LLMClient(config)
            with (
                patch("time.sleep"),
                pytest.raises(LLMRequestError, match="Connection failed"),
            ):
                client.chat([{"role": "user", "content": "test"}])

            assert mock_post.call_count == config.max_retries


class TestExtractContentErrors:
    def test_raises_on_malformed_response(self) -> None:
        # Response where choices is not a list, causing TypeError on indexing
        with pytest.raises(LLMResponseError, match="Failed to parse response"):
            _extract_content({"choices": 123})


class TestChatFunction:
    def test_chat_function(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("LLM_API_KEY", "test-key")

        with patch.object(httpx.Client, "post") as mock_post:
            mock_resp = MagicMock()
            mock_resp.json.return_value = {"choices": [{"message": {"content": "response"}}]}
            mock_resp.raise_for_status.return_value = None
            mock_post.return_value = mock_resp

            result = chat([{"role": "user", "content": "test"}])

            assert result == "response"
