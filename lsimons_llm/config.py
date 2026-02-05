"""Configuration for LLM client.

Supports configuration via environment variables:
- LLM_BASE_URL: API endpoint (default: https://litellm.sbp.ai/v1)
- LLM_API_KEY: API key for authentication (required)
- LLM_MODEL: Model name (default: azure/gpt-4o-mini)
- LLM_MAX_TOKENS: Maximum tokens per request (default: 4096)
- LLM_TEMPERATURE: Sampling temperature (default: 0.7)
- LLM_TIMEOUT: Request timeout in seconds (default: 120)
- LLM_MAX_RETRIES: Maximum retry attempts (default: 3)
"""

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class LLMConfig:
    """Configuration for LLM client.

    Attributes:
        base_url: API endpoint URL
        api_key: API key for authentication
        model: Model name
        max_tokens: Maximum tokens per request
        temperature: Sampling temperature (0.0-1.0)
        timeout: Request timeout in seconds
        max_retries: Maximum retry attempts
    """

    base_url: str
    api_key: str
    model: str
    max_tokens: int
    temperature: float
    timeout: int
    max_retries: int


def load_config(
    base_url: str | None = None,
    api_key: str | None = None,
    model: str | None = None,
    max_tokens: int | None = None,
    temperature: float | None = None,
    timeout: int | None = None,
    max_retries: int | None = None,
) -> LLMConfig:
    """Load LLM configuration from environment with optional overrides.

    Arguments take precedence over environment variables.

    Args:
        base_url: API endpoint URL (overrides LLM_BASE_URL)
        api_key: API key (overrides LLM_API_KEY)
        model: Model name (overrides LLM_MODEL)
        max_tokens: Max tokens (overrides LLM_MAX_TOKENS)
        temperature: Temperature (overrides LLM_TEMPERATURE)
        timeout: Timeout in seconds (overrides LLM_TIMEOUT)
        max_retries: Max retries (overrides LLM_MAX_RETRIES)

    Returns:
        LLMConfig instance

    Raises:
        ValueError: If api_key is not provided and LLM_API_KEY is not set
    """
    resolved_api_key = api_key or os.environ.get("LLM_API_KEY", "")
    if not resolved_api_key:
        raise ValueError(
            "API key required. Set LLM_API_KEY environment variable or pass api_key argument."
        )

    return LLMConfig(
        base_url=base_url or os.environ.get("LLM_BASE_URL", "https://litellm.sbp.ai/v1"),
        api_key=resolved_api_key,
        model=model or os.environ.get("LLM_MODEL", "azure/gpt-4o-mini"),
        max_tokens=max_tokens or int(os.environ.get("LLM_MAX_TOKENS", "4096")),
        temperature=temperature or float(os.environ.get("LLM_TEMPERATURE", "0.7")),
        timeout=timeout or int(os.environ.get("LLM_TIMEOUT", "120")),
        max_retries=max_retries or int(os.environ.get("LLM_MAX_RETRIES", "3")),
    )
