from functools import lru_cache
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """All configuration comes from environment variables (prefix-free) or a .env file."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    environment: Literal["development", "test", "production"] = "development"
    database_url: str = "sqlite:///./intel.db"
    storage_dir: str = "./storage"
    cors_origins: list[str] = Field(default_factory=lambda: ["http://localhost:3000"])

    # Authentication. "supabase" verifies Supabase-issued JWTs; "dev" accepts tokens signed with
    # dev_jwt_secret and is refused when environment == "production".
    auth_mode: Literal["supabase", "dev"] = "dev"
    supabase_url: str | None = None
    supabase_jwt_secret: str | None = None
    supabase_jwt_audience: str = "authenticated"
    dev_jwt_secret: str = "dev-only-secret-change-me-at-least-32-bytes"  # noqa: S105 - refused in production

    # Providers. Missing keys make runs fail with a clear error; nothing is simulated.
    tavily_api_key: str | None = None
    gemini_api_key: str | None = None
    llm_model: str = "gemini-3.8-flash"
    # Tried in order when the main model stays overloaded (HTTP 429/503) after all retries.
    llm_fallback_models: list[str] = Field(default_factory=list)
    llm_attempts: int = 5
    embedding_model: str = "gemini-embedding-001"

    # Limits.
    rate_limit_per_minute: int = 60
    runs_per_workspace_per_month: int = 50
    max_searches_per_run: int = 20
    max_upload_mb: int = 25
    max_pdf_pages: int = 400
    max_claims_per_run: int = 60

    # Evidence thresholds, versioned with each run.
    support_threshold: float = 0.70
    partial_threshold: float = 0.40

    # Run research jobs in a thread inside the API process (single-container deploys).
    # Set to false when running `python -m intel.worker` separately.
    worker_in_process: bool = True

    terms_version: str = "2026-10-21"
    privacy_version: str = "2026-10-21"


@lru_cache
def get_settings() -> Settings:
    return Settings()
