import sys
from types import ModuleType, SimpleNamespace
from unittest.mock import Mock

import pytest

from triage.auth import AuthenticationError, DEFAULT_AZURE_SCOPE, live_api_key
from triage.providers import LiveClassifier


@pytest.fixture(autouse=True)
def isolate_auth_environment(monkeypatch):
    for key in ("OPENAI_AUTH_MODE", "OPENAI_API_KEY", "AZURE_TENANT_ID", "AZURE_TOKEN_SCOPE"):
        monkeypatch.delenv(key, raising=False)


@pytest.fixture
def identity(monkeypatch):
    class ClientAuthenticationError(Exception):
        pass

    identity_module = ModuleType("azure.identity")
    identity_module.AzureCliCredential = Mock()
    identity_module.get_bearer_token_provider = Mock(return_value=Mock(return_value="synthetic-token"))
    exceptions = ModuleType("azure.core.exceptions")
    exceptions.ClientAuthenticationError = ClientAuthenticationError
    for name, module in {
        "azure": ModuleType("azure"),
        "azure.core": ModuleType("azure.core"),
        "azure.core.exceptions": exceptions,
        "azure.identity": identity_module,
    }.items():
        monkeypatch.setitem(sys.modules, name, module)
    return SimpleNamespace(
        credential=identity_module.AzureCliCredential,
        provider=identity_module.get_bearer_token_provider,
        error=ClientAuthenticationError,
    )


def test_api_key_remains_default(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "synthetic-key")
    assert live_api_key() == "synthetic-key"


def test_api_key_mode_requires_key():
    with pytest.raises(RuntimeError, match="OPENAI_API_KEY"):
        live_api_key()


def test_invalid_auth_mode_does_not_fall_back(monkeypatch):
    monkeypatch.setenv("OPENAI_AUTH_MODE", "typo")
    monkeypatch.setenv("OPENAI_API_KEY", "synthetic-key")
    with pytest.raises(RuntimeError, match="no automatic fallback"):
        live_api_key()


def test_azure_cli_needs_no_key_and_passes_scope_and_tenant(monkeypatch, identity):
    monkeypatch.setenv("OPENAI_AUTH_MODE", "azure-cli")
    monkeypatch.setenv("AZURE_TENANT_ID", "synthetic-tenant")
    provider = live_api_key()
    assert callable(provider)
    identity.credential.assert_called_once_with(tenant_id="synthetic-tenant", process_timeout=30)
    identity.provider.assert_called_once_with(identity.credential.return_value, DEFAULT_AZURE_SCOPE)
    identity.provider.return_value.assert_not_called()
    assert provider() == "synthetic-token"


def test_azure_cli_ignores_key_and_keeps_refresh_callback(monkeypatch, identity):
    monkeypatch.setenv("OPENAI_AUTH_MODE", "azure-cli")
    monkeypatch.setenv("OPENAI_API_KEY", "must-not-be-used")
    monkeypatch.setenv("AZURE_TOKEN_SCOPE", "api://synthetic-gateway/.default")
    identity.provider.return_value.side_effect = ["token-before-expiry", "token-after-refresh"]
    provider = live_api_key()
    assert callable(provider)
    assert provider() == "token-before-expiry"
    assert provider() == "token-after-refresh"
    identity.provider.assert_called_once_with(
        identity.credential.return_value, "api://synthetic-gateway/.default"
    )


@pytest.mark.parametrize("scope", ["", " ", "https://ai.azure.com", "a/.default b/.default"])
def test_invalid_scope_is_explicit(monkeypatch, identity, scope):
    monkeypatch.setenv("OPENAI_AUTH_MODE", "azure-cli")
    monkeypatch.setenv("AZURE_TOKEN_SCOPE", scope)
    with pytest.raises(RuntimeError, match="AZURE_TOKEN_SCOPE"):
        live_api_key()
    identity.credential.assert_not_called()


def test_auth_failure_does_not_leak_details_or_use_key(monkeypatch, identity):
    monkeypatch.setenv("OPENAI_AUTH_MODE", "azure-cli")
    monkeypatch.setenv("OPENAI_API_KEY", "must-not-be-used")
    identity.provider.return_value.side_effect = identity.error("sensitive upstream content")
    provider = live_api_key()
    with pytest.raises(AuthenticationError, match="az login") as caught:
        provider()
    assert "sensitive upstream content" not in str(caught.value)
    assert "must-not-be-used" not in str(caught.value)


def test_live_client_receives_callable_not_static_token(monkeypatch, identity):
    monkeypatch.setenv("OPENAI_AUTH_MODE", "azure-cli")
    monkeypatch.setenv("OPENAI_BASE_URL", "https://example.test/openai/v1/")
    monkeypatch.setenv("OPENAI_MODEL", "synthetic-model")
    langchain = ModuleType("langchain_openai")
    langchain.ChatOpenAI = Mock()
    monkeypatch.setitem(sys.modules, "langchain_openai", langchain)
    LiveClassifier()
    key = langchain.ChatOpenAI.call_args.kwargs["api_key"]
    assert callable(key)
    identity.provider.return_value.assert_not_called()
    assert key() == "synthetic-token"


def test_auth_failure_becomes_explicit_http_error(monkeypatch, caplog):
    from triage.app import create_app

    openai = ModuleType("openai")
    openai.APIError = type("APIError", (Exception,), {})
    monkeypatch.setitem(sys.modules, "openai", openai)
    provider = LiveClassifier.__new__(LiveClassifier)
    provider.client = Mock()
    provider.client.invoke.side_effect = AuthenticationError("Azure CLI authentication failed. Run az login.")
    response = create_app(provider).test_client().post(
        "/api/triage", json={"store_id": "store-001", "text": "Proszę o kontakt."}
    )
    assert response.status_code == 502
    assert "az login" in response.json["error"]
    assert "jira_draft" not in response.json
    assert "ProviderError" in caplog.text
