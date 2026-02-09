"""Asynchronous LLM client using the OpenAI SDK.

Requires the 'async' extra: pip install lsimons-llm[async]
"""

from typing import TYPE_CHECKING, Any

from lsimons_llm.config import LLMConfig
from lsimons_llm.exceptions import LLMRequestError, LLMResponseError

if TYPE_CHECKING:
    from openai.types.chat import ChatCompletionMessageParam


class AsyncLLMClient:
    """Asynchronous client for OpenAI-compatible LLM APIs.

    Uses the official OpenAI SDK for async support.

    Example:
        >>> config = load_config()
        >>> client = AsyncLLMClient(config)
        >>> response = await client.chat([{"role": "user", "content": "Hello"}])
        >>> print(response)
    """

    def __init__(self, config: LLMConfig) -> None:
        """Initialize the async client with configuration.

        Args:
            config: LLM configuration instance

        Raises:
            ImportError: If openai package is not installed
        """
        try:
            from openai import AsyncOpenAI
        except ImportError as e:
            raise ImportError(
                "openai package required for async client. "
                "Install with: pip install lsimons-llm[async]"
            ) from e

        self.config = config
        self._client: AsyncOpenAI = AsyncOpenAI(
            base_url=config.base_url,
            api_key=config.api_key,
            timeout=float(config.timeout),
            max_retries=config.max_retries,
        )

    async def chat(
        self,
        messages: list[dict[str, Any]],
        model: str | None = None,
        temperature: float | None = None,
        max_tokens: int | None = None,
    ) -> str:
        """Send chat messages and return the assistant's response content.

        Args:
            messages: List of message dicts with 'role' and 'content' keys
            model: Override default model
            temperature: Override default temperature
            max_tokens: Override default max_tokens

        Returns:
            The assistant's response content as a string

        Raises:
            LLMRequestError: If the request fails
            LLMResponseError: If the response cannot be parsed
        """
        try:
            # Cast messages to the expected type
            typed_messages: list[ChatCompletionMessageParam] = [
                {"role": m["role"], "content": m["content"]}  # type: ignore[typeddict-item]
                for m in messages
            ]

            response = await self._client.chat.completions.create(
                model=model or self.config.model,
                messages=typed_messages,
                temperature=temperature or self.config.temperature,
                max_tokens=max_tokens or self.config.max_tokens,
            )

            if not response.choices:
                raise LLMResponseError("No choices in response")

            content = response.choices[0].message.content
            if content is None:
                raise LLMResponseError("No content in response message")

            return content

        except LLMResponseError:
            raise
        except Exception as e:
            raise LLMRequestError(str(e)) from e

    async def close(self) -> None:
        """Close the async HTTP client."""
        await self._client.close()

    async def __aenter__(self) -> AsyncLLMClient:
        return self

    async def __aexit__(self, *args: object) -> None:
        await self.close()
