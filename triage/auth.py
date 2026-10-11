import os
from collections.abc import Callable
from pathlib import Path


DEFAULT_AZURE_SCOPE = "https://ai.azure.com/.default"


class AuthenticationError(RuntimeError):
    pass


def live_api_key() -> str | Callable[[], str]:
    mode = os.environ.get("OPENAI_AUTH_MODE", "api-key")
    if mode == "api-key":
        key = os.environ.get("OPENAI_API_KEY", "").strip()
        if not key:
            raise RuntimeError("Missing live configuration: OPENAI_API_KEY")
        return key
    if mode != "azure-cli":
        raise RuntimeError("OPENAI_AUTH_MODE must be api-key or azure-cli; no automatic fallback.")

    from azure.core.exceptions import ClientAuthenticationError
    from azure.identity import AzureCliCredential, get_bearer_token_provider

    scope = os.environ.get("AZURE_TOKEN_SCOPE", DEFAULT_AZURE_SCOPE).strip()
    if not scope.endswith("/.default") or any(char.isspace() for char in scope):
        raise RuntimeError("AZURE_TOKEN_SCOPE must be one nonempty resource scope ending in /.default.")
    credential = AzureCliCredential(
        tenant_id=os.environ.get("AZURE_TENANT_ID", "").strip(),
        process_timeout=30,
    )
    token_provider = get_bearer_token_provider(credential, scope)

    def token() -> str:
        try:
            return token_provider()
        except ClientAuthenticationError:
            raise AuthenticationError(
                "Azure CLI authentication failed. Run az login for the endpoint tenant "
                "and check AZURE_TENANT_ID / AZURE_TOKEN_SCOPE. No API-key fallback."
            ) from None

    return token


def main() -> None:
    from dotenv import load_dotenv

    load_dotenv(Path(__file__).resolve().parent.parent / ".env", override=False)
    if os.environ.get("OPENAI_AUTH_MODE") != "azure-cli":
        raise SystemExit("Set OPENAI_AUTH_MODE=azure-cli before checking the local Azure session.")
    try:
        provider = live_api_key()
        if not callable(provider):
            raise RuntimeError("Expected an Azure token provider.")
        provider()
    except RuntimeError as exc:
        raise SystemExit(str(exc)) from None
    print("PASS: Azure CLI token acquired (not displayed or saved). Endpoint access / RBAC not checked.")


if __name__ == "__main__":
    main()
