class ProviderError(RuntimeError):
    """A provider call failed. The message is safe to show to users."""


class ProviderNotConfigured(ProviderError):
    pass
