"""API server for browser end-to-end tests: real app and database, fake model and search.

Run: python -m tests.e2e_server  (listens on E2E_PORT, default 8010). Never use outside tests.
"""

import os
import tempfile

import uvicorn

tmp = tempfile.mkdtemp(prefix="intel-e2e-")
os.environ.update(
    ENVIRONMENT="test",
    AUTH_MODE="dev",
    DATABASE_URL=f"sqlite:///{tmp}/e2e.db",
    STORAGE_DIR=f"{tmp}/storage",
    WORKER_IN_PROCESS="true",
    CORS_ORIGINS='["http://localhost:3010","http://127.0.0.1:3010"]',
)

from intel.main import create_app  # noqa: E402
from intel.pipeline.orchestrator import Providers  # noqa: E402
from intel.providers import factory  # noqa: E402
from tests.fakes import FakeLLM, FakeSearch  # noqa: E402

factory.set_factory(lambda s: Providers(llm=FakeLLM(), search=FakeSearch()))

if __name__ == "__main__":
    uvicorn.run(create_app(), host="127.0.0.1", port=int(os.environ.get("E2E_PORT", "8010")), log_level="warning")
