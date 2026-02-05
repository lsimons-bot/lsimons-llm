"""Custom exceptions for LLM client operations."""


class LLMError(Exception):
    """Base exception for LLM client errors."""


class LLMRequestError(LLMError):
    """Raised when an LLM request fails."""

    def __init__(self, message: str, status_code: int | None = None) -> None:
        super().__init__(message)
        self.status_code = status_code


class LLMResponseError(LLMError):
    """Raised when an LLM response cannot be parsed or is invalid."""
