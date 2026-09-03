"""Social-login provider boundary for Google and Facebook callback adapters."""


async def exchange_provider_code(provider: str, code: str) -> dict[str, str]:
    """Exchange a provider authorization code; wire an audited OAuth client here."""
    if provider not in {"google", "facebook"}:
        raise ValueError("Unsupported provider")
    raise NotImplementedError("Configure the provider client for this deployment")
