"""Synchronous LLM client for OpenAI-compatible APIs."""

import time
from typing import Any

import httpx

from lsimons_llm.config import LLMConfig, load_config
from lsimons_llm.exceptions import LLMRequestError, LLMResponseError


class LLMClient:
    """Synchronous client for OpenAI-compatible LLM APIs.

    Example:
        >>> config = load_config()
        >>> client = LLMClient(config)
        >>> response = client.chat([{"role": "user", "content": "Hello"}])
        >>> print(response)
    """

    def __init__(self, config: LLMConfig) -> None:
        """Initialize the client with configuration.

        Args:
            config: LLM configuration instance
        """
        self.config = config
        self._client = httpx.Client(timeout=config.timeout)

    def chat(
        self,
        messages: list[dict[str, Any]],
        tools: list[dict[str, Any]] | None = None,
        model: str | None = None,
        temperature: float | None = None,
        max_tokens: int | None = None,
    ) -> str:
        """Send chat messages and return the assistant's response content.

        Args:
            messages: List of message dicts with 'role' and 'content' keys
            tools: Optional list of tool definitions for function calling
            model: Override default model
            temperature: Override default temperature
            max_tokens: Override default max_tokens

        Returns:
            The assistant's response content as a string

        Raises:
            LLMRequestError: If the request fails after retries
            LLMResponseError: If the response cannot be parsed
        """
        response = self.chat_raw(messages, tools, model, temperature, max_tokens)
        return _extract_content(response)

    def chat_raw(
        self,
        messages: list[dict[str, Any]],
        tools: list[dict[str, Any]] | None = None,
        model: str | None = None,
        temperature: float | None = None,
        max_tokens: int | None = None,
    ) -> dict[str, Any]:
        """Send chat messages and return the raw API response.

        Args:
            messages: List of message dicts with 'role' and 'content' keys
            tools: Optional list of tool definitions for function calling
            model: Override default model
            temperature: Override default temperature
            max_tokens: Override default max_tokens

        Returns:
            Raw API response dict

        Raises:
            LLMRequestError: If the request fails after retries
        """
        payload: dict[str, Any] = {
            "model": model or self.config.model,
            "messages": messages,
            "max_tokens": max_tokens or self.config.max_tokens,
            "temperature": temperature or self.config.temperature,
        }
        if tools:
            payload["tools"] = tools

        headers = {"Authorization": f"Bearer {self.config.api_key}"}
        url = f"{self.config.base_url.rstrip('/')}/chat/completions"

        last_error: Exception | None = None
        for attempt in range(self.config.max_retries):
            try:
                response = self._client.post(url, json=payload, headers=headers)
                response.raise_for_status()
                result: dict[str, Any] = response.json()
                return result
            except httpx.HTTPStatusError as e:
                last_error = LLMRequestError(str(e), status_code=e.response.status_code)
                if e.response.status_code < 500:
                    raise last_error from e
            except httpx.RequestError as e:
                last_error = LLMRequestError(str(e))

            if attempt < self.config.max_retries - 1:
                time.sleep(2**attempt)

        raise last_error or LLMRequestError("Request failed")

    def close(self) -> None:
        """Close the HTTP client."""
        self._client.close()

    def __enter__(self) -> LLMClient:
        return self

    def __exit__(self, *args: object) -> None:
        self.close()


def chat(
    messages: list[dict[str, Any]],
    tools: list[dict[str, Any]] | None = None,
    model: str | None = None,
    temperature: float | None = None,
    max_tokens: int | None = None,
) -> str:
    """Convenience function for one-off chat requests.

    Loads configuration from environment and sends a chat request.

    Args:
        messages: List of message dicts with 'role' and 'content' keys
        tools: Optional list of tool definitions for function calling
        model: Override default model
        temperature: Override default temperature
        max_tokens: Override default max_tokens

    Returns:
        The assistant's response content as a string

    Raises:
        ValueError: If LLM_API_KEY is not set
        LLMRequestError: If the request fails
        LLMResponseError: If the response cannot be parsed
    """
    config = load_config()
    with LLMClient(config) as client:
        return client.chat(messages, tools, model, temperature, max_tokens)


def _extract_content(response: dict[str, Any]) -> str:
    """Extract content from API response.

    Args:
        response: Raw API response dict

    Returns:
        The content string from the first choice

    Raises:
        LLMResponseError: If content cannot be extracted
    """
    try:
        choices = response.get("choices", [])
        if not choices:
            raise LLMResponseError("No choices in response")
        message = choices[0].get("message", {})
        content = message.get("content")
        if content is None:
            raise LLMResponseError("No content in response message")
        return str(content)
    except (KeyError, IndexError, TypeError) as e:
        raise LLMResponseError(f"Failed to parse response: {e}") from e
