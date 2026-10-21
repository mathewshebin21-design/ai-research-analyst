"""Builds real providers from settings. Tests replace `build` with fakes."""

from collections.abc import Callable

from intel.config import Settings
from intel.pipeline.orchestrator import Providers
from intel.providers.llm import GeminiLLM
from intel.providers.search import TavilyClient


def _default(settings: Settings) -> Providers:
    return Providers(
        llm=GeminiLLM(settings.gemini_api_key, settings.llm_model), search=TavilyClient(settings.tavily_api_key)
    )


build: Callable[[Settings], Providers] = _default


def set_factory(fn: Callable[[Settings], Providers]) -> None:
    global build
    build = fn


def get_providers(settings: Settings) -> Providers:
    return build(settings)
