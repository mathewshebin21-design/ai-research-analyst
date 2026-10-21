import os

import pytest
from fastapi.testclient import TestClient


@pytest.fixture()
def settings_env(tmp_path, monkeypatch):
    monkeypatch.setenv("ENVIRONMENT", "test")
    monkeypatch.setenv("AUTH_MODE", "dev")
    # CI also runs the suite against Postgres by setting TEST_DATABASE_URL.
    monkeypatch.setenv("DATABASE_URL", os.environ.get("TEST_DATABASE_URL") or f"sqlite:///{tmp_path}/test.db")
    monkeypatch.setenv("STORAGE_DIR", str(tmp_path / "storage"))
    monkeypatch.setenv("WORKER_IN_PROCESS", "false")
    monkeypatch.setenv("RATE_LIMIT_PER_MINUTE", "1000")
    from intel.api import deps
    from intel.config import get_settings

    get_settings.cache_clear()
    deps._limiters.clear()
    yield tmp_path
    get_settings.cache_clear()


@pytest.fixture()
def fake_providers():
    from intel.pipeline.orchestrator import Providers
    from intel.providers import factory
    from tests.fakes import FakeLLM, FakeSearch

    search = FakeSearch()
    original = factory.build
    factory.set_factory(lambda s: Providers(llm=FakeLLM(), search=search))
    yield search
    factory.set_factory(original)


@pytest.fixture()
def client(settings_env, fake_providers):
    from intel.db import Base, init_engine
    from intel.main import create_app

    engine = init_engine(os.environ["DATABASE_URL"])
    if engine.dialect.name != "sqlite":
        Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    with TestClient(create_app(start_worker=False)) as c:
        yield c


def login(client, email="ana@example.com", accept=True) -> dict:
    token = client.post("/dev/token", json={"email": email}).json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    if accept:
        v = client.get("/legal/versions").json()
        r = client.post(
            "/me/accept-terms", json={"terms_version": v["terms"], "privacy_version": v["privacy"]}, headers=headers
        )
        assert r.status_code == 200, r.text
    return headers
