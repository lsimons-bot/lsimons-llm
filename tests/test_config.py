"""Tests for LLM configuration."""

import os

import pytest

from lsimons_llm.config import LLMConfig, load_config


class TestLLMConfig:
    def test_config_is_frozen(self) -> None:
        config = LLMConfig(
            base_url="http://test",
            api_key="key",
            model="model",
            max_tokens=100,
            temperature=0.5,
            timeout=30,
            max_retries=2,
        )
        with pytest.raises(AttributeError):
            config.api_key = "new"  # type: ignore[misc]


class TestLoadConfig:
    def test_load_config_from_env(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("LLM_API_KEY", "test-key")
        monkeypatch.setenv("LLM_BASE_URL", "http://test-url")
        monkeypatch.setenv("LLM_MODEL", "test-model")
        monkeypatch.setenv("LLM_MAX_TOKENS", "1000")
        monkeypatch.setenv("LLM_TEMPERATURE", "0.5")
        monkeypatch.setenv("LLM_TIMEOUT", "60")
        monkeypatch.setenv("LLM_MAX_RETRIES", "5")

        config = load_config()

        assert config.api_key == "test-key"
        assert config.base_url == "http://test-url"
        assert config.model == "test-model"
        assert config.max_tokens == 1000
        assert config.temperature == 0.5
        assert config.timeout == 60
        assert config.max_retries == 5

    def test_load_config_defaults(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("LLM_API_KEY", "test-key")
        # Clear other env vars
        for var in ["LLM_BASE_URL", "LLM_MODEL", "LLM_MAX_TOKENS", "LLM_TEMPERATURE"]:
            monkeypatch.delenv(var, raising=False)

        config = load_config()

        assert config.base_url == "https://litellm.sbp.ai/v1"
        assert config.model == "azure/gpt-4o-mini"
        assert config.max_tokens == 4096
        assert config.temperature == 0.7

    def test_load_config_argument_override(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("LLM_API_KEY", "env-key")
        monkeypatch.setenv("LLM_MODEL", "env-model")

        config = load_config(api_key="arg-key", model="arg-model")

        assert config.api_key == "arg-key"
        assert config.model == "arg-model"

    def test_load_config_requires_api_key(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.delenv("LLM_API_KEY", raising=False)

        with pytest.raises(ValueError, match="API key required"):
            load_config()

    def test_load_config_api_key_from_argument(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.delenv("LLM_API_KEY", raising=False)

        config = load_config(api_key="provided-key")

        assert config.api_key == "provided-key"
