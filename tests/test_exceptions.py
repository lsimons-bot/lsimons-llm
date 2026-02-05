"""Tests for LLM exceptions."""

from lsimons_llm.exceptions import LLMError, LLMRequestError, LLMResponseError


class TestExceptions:
    def test_llm_error_is_exception(self) -> None:
        assert issubclass(LLMError, Exception)

    def test_request_error_inherits_from_llm_error(self) -> None:
        assert issubclass(LLMRequestError, LLMError)

    def test_response_error_inherits_from_llm_error(self) -> None:
        assert issubclass(LLMResponseError, LLMError)

    def test_request_error_with_status_code(self) -> None:
        error = LLMRequestError("Bad request", status_code=400)
        assert str(error) == "Bad request"
        assert error.status_code == 400

    def test_request_error_without_status_code(self) -> None:
        error = LLMRequestError("Connection failed")
        assert str(error) == "Connection failed"
        assert error.status_code is None
