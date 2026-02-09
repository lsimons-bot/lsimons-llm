"""Tests for asynchronous LLM client."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

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
def mock_response() -> MagicMock:
    response = MagicMock()
    response.choices = [MagicMock(message=MagicMock(content="Hello! How can I help?"))]
    return response


class TestAsyncLLMClient:
    async def test_chat_returns_content(self, config: LLMConfig, mock_response: MagicMock) -> None:
        with (
            patch.dict("sys.modules", {"openai": MagicMock()}),
            patch("openai.AsyncOpenAI") as mock_openai,
        ):
            mock_client = MagicMock()
            mock_client.chat.completions.create = AsyncMock(return_value=mock_response)
            mock_client.close = AsyncMock()
            mock_openai.return_value = mock_client

            from lsimons_llm.async_client import AsyncLLMClient

            client = AsyncLLMClient(config)
            result = await client.chat([{"role": "user", "content": "Hi"}])

            assert result == "Hello! How can I help?"

    async def test_chat_with_overrides(self, config: LLMConfig, mock_response: MagicMock) -> None:
        with (
            patch.dict("sys.modules", {"openai": MagicMock()}),
            patch("openai.AsyncOpenAI") as mock_openai,
        ):
            mock_client = MagicMock()
            mock_client.chat.completions.create = AsyncMock(return_value=mock_response)
            mock_client.close = AsyncMock()
            mock_openai.return_value = mock_client

            from lsimons_llm.async_client import AsyncLLMClient

            client = AsyncLLMClient(config)
            await client.chat(
                [{"role": "user", "content": "test"}],
                model="override-model",
                temperature=0.9,
                max_tokens=500,
            )

            call_args = mock_client.chat.completions.create.call_args
            assert call_args[1]["model"] == "override-model"
            assert call_args[1]["temperature"] == 0.9
            assert call_args[1]["max_tokens"] == 500

    async def test_chat_raises_on_no_choices(self, config: LLMConfig) -> None:
        with (
            patch.dict("sys.modules", {"openai": MagicMock()}),
            patch("openai.AsyncOpenAI") as mock_openai,
        ):
            no_choices_response = MagicMock()
            no_choices_response.choices = []

            mock_client = MagicMock()
            mock_client.chat.completions.create = AsyncMock(return_value=no_choices_response)
            mock_client.close = AsyncMock()
            mock_openai.return_value = mock_client

            from lsimons_llm.async_client import AsyncLLMClient

            client = AsyncLLMClient(config)
            with pytest.raises(LLMResponseError, match="No choices"):
                await client.chat([{"role": "user", "content": "test"}])

    async def test_chat_raises_on_no_content(self, config: LLMConfig) -> None:
        with (
            patch.dict("sys.modules", {"openai": MagicMock()}),
            patch("openai.AsyncOpenAI") as mock_openai,
        ):
            no_content_response = MagicMock()
            no_content_response.choices = [MagicMock(message=MagicMock(content=None))]

            mock_client = MagicMock()
            mock_client.chat.completions.create = AsyncMock(return_value=no_content_response)
            mock_client.close = AsyncMock()
            mock_openai.return_value = mock_client

            from lsimons_llm.async_client import AsyncLLMClient

            client = AsyncLLMClient(config)
            with pytest.raises(LLMResponseError, match="No content"):
                await client.chat([{"role": "user", "content": "test"}])

    async def test_chat_raises_request_error_on_exception(self, config: LLMConfig) -> None:
        with (
            patch.dict("sys.modules", {"openai": MagicMock()}),
            patch("openai.AsyncOpenAI") as mock_openai,
        ):
            mock_client = MagicMock()
            mock_client.chat.completions.create = AsyncMock(side_effect=Exception("API error"))
            mock_client.close = AsyncMock()
            mock_openai.return_value = mock_client

            from lsimons_llm.async_client import AsyncLLMClient

            client = AsyncLLMClient(config)
            with pytest.raises(LLMRequestError, match="API error"):
                await client.chat([{"role": "user", "content": "test"}])

    async def test_context_manager(self, config: LLMConfig, mock_response: MagicMock) -> None:
        with (
            patch.dict("sys.modules", {"openai": MagicMock()}),
            patch("openai.AsyncOpenAI") as mock_openai,
        ):
            mock_client = MagicMock()
            mock_client.chat.completions.create = AsyncMock(return_value=mock_response)
            mock_client.close = AsyncMock()
            mock_openai.return_value = mock_client

            from lsimons_llm.async_client import AsyncLLMClient

            async with AsyncLLMClient(config) as client:
                assert isinstance(client, AsyncLLMClient)

            mock_client.close.assert_called_once()


class TestAsyncLLMClientImportError:
    def test_raises_import_error_when_openai_not_installed(self, config: LLMConfig) -> None:
        import sys

        # Temporarily remove openai from modules if present
        openai_module = sys.modules.get("openai")
        sys.modules["openai"] = None  # type: ignore[assignment]

        try:
            # Force reimport to trigger the ImportError
            import importlib

            import lsimons_llm.async_client

            importlib.reload(lsimons_llm.async_client)

            with pytest.raises(ImportError, match="openai package required"):
                lsimons_llm.async_client.AsyncLLMClient(config)
        finally:
            # Restore the module
            if openai_module is not None:
                sys.modules["openai"] = openai_module
            elif "openai" in sys.modules:
                del sys.modules["openai"]
