class ProviderError(RuntimeError):
    """A provider call failed. The message is safe to show to users."""


class ProviderNotConfigured(ProviderError):
    pass


class ProviderQuotaExceeded(ProviderError):
    """The account's quota is used up (e.g. a free-tier daily limit). Retrying or continuing will not help."""
