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
    def __init__(self, api_key: str | None, model: str, attempts: int = 5) -> None:
        if not api_key:
            raise ProviderNotConfigured("GEMINI_API_KEY is not set, so research runs cannot start.")
        from google import genai

        self._client = genai.Client(api_key=api_key)
        self.model = model
        self.attempts = attempts

    def generate(self, *, system: str, prompt: str, schema: type[T], usage: Usage, temperature: float = 0.2) -> T:
        from google.genai import errors as genai_errors
        from google.genai import types

        config = types.GenerateContentConfig(
            system_instruction=system,
            temperature=temperature,
            response_mime_type="application/json",
            response_schema=schema,
        )
        last: Exception | None = None
        for attempt in range(self.attempts):
            try:
                response = self._client.models.generate_content(model=self.model, contents=prompt, config=config)
                usage.llm_calls += 1
                meta = response.usage_metadata
                if meta is not None:
                    usage.input_tokens += meta.prompt_token_count or 0
                    usage.output_tokens += meta.candidates_token_count or 0
                if isinstance(response.parsed, schema):
                    return response.parsed
                return schema.model_validate(json.loads(response.text or ""))
            except (ValidationError, json.JSONDecodeError) as exc:
                last = exc
                log.warning("model returned invalid structure", extra={"stage": schema.__name__})
            except genai_errors.APIError as exc:
                last = exc
                if getattr(exc, "code", 500) not in (429, 500, 502, 503, 504):
                    break
            if attempt < self.attempts - 1:
                time.sleep(min(30.0, 2.0 * (2**attempt)))  # 2, 4, 8, 16 s: rides out short overload spikes
        detail = type(last).__name__
        if last is not None and hasattr(last, "code"):
            # Status and Google's message help fix configuration (bad key, API disabled, quota).
            # Neither contains the key.
            code, status = getattr(last, "code", "?"), getattr(last, "status", "") or ""
            message = str(getattr(last, "message", "") or last)[:300]
            detail = f"HTTP {code} {status}: {message}"
        raise ProviderError(f"The language model failed for {schema.__name__} ({detail})") from last
