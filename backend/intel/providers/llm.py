"""Language-model adapter. Every call returns a validated Pydantic object or raises."""

import json
import logging
import time
from typing import Protocol, TypeVar

from pydantic import BaseModel, ValidationError

from intel.providers.errors import ProviderError, ProviderNotConfigured
from intel.providers.usage import Usage

T = TypeVar("T", bound=BaseModel)
log = logging.getLogger(__name__)


class LLM(Protocol):
    model: str

    def generate(self, *, system: str, prompt: str, schema: type[T], usage: Usage, temperature: float = 0.2) -> T: ...


class GeminiLLM:
    """Gemini via google-genai. Overload (429/503) is retried with backoff, then the next fallback model is tried."""

    RETRYABLE = (429, 500, 502, 503, 504)

    def __init__(self, api_key: str | None, model: str, attempts: int = 5, fallbacks: list[str] | None = None) -> None:
        if not api_key:
            raise ProviderNotConfigured("GEMINI_API_KEY is not set, so research runs cannot start.")
        from google import genai
        from google.genai import types

        # Our own retry loop decides when to back off or fall back; the SDK's built-in retries would
        # multiply the wait (seen as 30-minute stalls during overload). Each request times out at 2 minutes.
        options = types.HttpOptions(retry_options=types.HttpRetryOptions(attempts=1), timeout=120_000)
        self._client = genai.Client(api_key=api_key, http_options=options)
        self.model = model
        self.models = [model, *[m for m in (fallbacks or []) if m and m != model]]
        self.attempts = attempts
        self.last_model = model

    def generate(self, *, system: str, prompt: str, schema: type[T], usage: Usage, temperature: float = 0.2) -> T:
        from google.genai import types

        config = types.GenerateContentConfig(
            system_instruction=system,
            temperature=temperature,
            response_mime_type="application/json",
            response_schema=schema,
        )
        last: Exception | None = None
        for model in self.models:
            result, last, retryable = self._try_model(model, prompt, config, schema, usage)
            if result is not None:
                self.last_model = model
                return result
            if not retryable:
                break  # configuration or request errors will not improve on another model
            log.warning("model unavailable, trying fallback", extra={"stage": schema.__name__})
        raise ProviderError(f"The language model failed for {schema.__name__} ({self._describe(last)})") from last

    def _try_model(self, model, prompt, config, schema, usage):
        from google.genai import errors as genai_errors

        last: Exception | None = None
        for attempt in range(self.attempts):
            try:
                response = self._client.models.generate_content(model=model, contents=prompt, config=config)
                usage.llm_calls += 1
                usage.models[model] = usage.models.get(model, 0) + 1
                meta = response.usage_metadata
                if meta is not None:
                    usage.input_tokens += meta.prompt_token_count or 0
                    usage.output_tokens += meta.candidates_token_count or 0
                if isinstance(response.parsed, schema):
                    return response.parsed, None, False
                return schema.model_validate(json.loads(response.text or "")), None, False
            except (ValidationError, json.JSONDecodeError) as exc:
                last = exc
                log.warning("model returned invalid structure", extra={"stage": schema.__name__})
            except genai_errors.APIError as exc:
                last = exc
                if getattr(exc, "code", 500) not in self.RETRYABLE:
                    return None, exc, False
            if attempt < self.attempts - 1:
                time.sleep(min(30.0, 2.0 * (2**attempt)))  # 2, 4, 8, 16, 30… s: rides out overload spikes
        return None, last, True

    @staticmethod
    def _describe(last: Exception | None) -> str:
        if last is None:
            return "no response"
        if hasattr(last, "code"):
            # Status and Google's message help fix configuration (bad key, model retired, quota).
            # Neither contains the key.
            code, status = getattr(last, "code", "?"), getattr(last, "status", "") or ""
            message = str(getattr(last, "message", "") or last)[:300]
            return f"HTTP {code} {status}: {message}"
        return type(last).__name__
