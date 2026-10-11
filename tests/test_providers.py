import sys
from types import ModuleType
from unittest.mock import Mock

import pytest

from triage.providers import DemoClassifier, LiveClassifier, build_classifier


def test_demo_mode(monkeypatch):
    monkeypatch.setenv("TRIAGE_MODE", "demo")
    assert isinstance(build_classifier(), DemoClassifier)


def test_unknown_mode_fails_explicitly(monkeypatch):
    monkeypatch.setenv("TRIAGE_MODE", "typo")
    with pytest.raises(RuntimeError, match="no automatic fallback"):
        build_classifier()


def test_live_configuration_is_required(monkeypatch):
    for key in ("OPENAI_BASE_URL", "OPENAI_API_KEY", "OPENAI_MODEL"):
        monkeypatch.delenv(key, raising=False)
    with pytest.raises(RuntimeError, match="Missing live configuration"):
        LiveClassifier()


def test_remote_http_endpoint_is_rejected(monkeypatch):
    monkeypatch.setenv("OPENAI_BASE_URL", "http://example.test/v1")
    monkeypatch.setenv("OPENAI_API_KEY", "synthetic-test-key")
    monkeypatch.setenv("OPENAI_MODEL", "synthetic-model")
    with pytest.raises(RuntimeError, match="HTTPS"):
        LiveClassifier()


@pytest.mark.parametrize("setting", ["", "invalid", "-1", "3", "nan", "inf"])
def test_invalid_temperature_fails_before_client_creation(monkeypatch, setting):
    monkeypatch.setenv("OPENAI_BASE_URL", "https://example.test/v1")
    monkeypatch.setenv("OPENAI_MODEL", "synthetic-model")
    monkeypatch.setenv("OPENAI_TEMPERATURE", setting)
    with pytest.raises(RuntimeError, match="OPENAI_TEMPERATURE"):
        LiveClassifier()


@pytest.mark.parametrize(("setting", "expected"), [(None, 0.0), ("0.5", 0.5), ("default", None)])
def test_temperature_can_use_server_default(monkeypatch, setting, expected):
    monkeypatch.setenv("OPENAI_BASE_URL", "https://example.test/v1")
    monkeypatch.setenv("OPENAI_MODEL", "synthetic-model")
    monkeypatch.setenv("OPENAI_AUTH_MODE", "api-key")
    monkeypatch.setenv("OPENAI_API_KEY", "synthetic-key")
    if setting is None:
        monkeypatch.delenv("OPENAI_TEMPERATURE", raising=False)
    else:
        monkeypatch.setenv("OPENAI_TEMPERATURE", setting)
    langchain = ModuleType("langchain_openai")
    langchain.ChatOpenAI = Mock()
    monkeypatch.setitem(sys.modules, "langchain_openai", langchain)
    LiveClassifier()
    assert langchain.ChatOpenAI.call_args.kwargs["temperature"] == expected
