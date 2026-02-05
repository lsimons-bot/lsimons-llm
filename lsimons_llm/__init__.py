"""Shared LLM client library for OpenAI-compatible APIs.

Provides both synchronous and asynchronous clients with unified configuration.
"""

from lsimons_llm.client import LLMClient, chat
from lsimons_llm.config import LLMConfig, load_config
from lsimons_llm.exceptions import LLMError, LLMRequestError, LLMResponseError

__all__ = [
    "LLMClient",
    "LLMConfig",
    "LLMError",
    "LLMRequestError",
    "LLMResponseError",
    "chat",
    "load_config",
]
