import logging
import time
import uuid
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import text

from intel.api import account, decision, documents, evidence, growth, runs, share, workspaces
from intel.config import get_settings
from intel.db import Base, get_engine
from intel.logging_setup import configure_logging, request_id
from intel.worker import start_in_process

log = logging.getLogger("intel.http")


def create_app(start_worker: bool | None = None) -> FastAPI:
    settings = get_settings()
    if settings.environment == "production" and settings.auth_mode == "dev":
        raise RuntimeError("AUTH_MODE=dev is not allowed in production.")

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        configure_logging()
        if settings.database_url.startswith("sqlite"):
            Base.metadata.create_all(get_engine())  # Postgres uses Alembic migrations instead.
        stop = start_in_process() if (settings.worker_in_process if start_worker is None else start_worker) else None
        yield
        if stop:
            stop.set()

    app = FastAPI(
        title="Strategic Intelligence Hub API",
        version="0.1.0",
        lifespan=lifespan,
        docs_url=None if settings.environment == "production" else "/docs",
        redoc_url=None,
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=False,
        allow_methods=["GET", "POST", "PUT", "DELETE"],
        allow_headers=["Authorization", "Content-Type"],
    )

    @app.middleware("http")
    async def context(request: Request, call_next):
        rid = request.headers.get("x-request-id") or uuid.uuid4().hex[:16]
        token = request_id.set(rid)
        start = time.perf_counter()
        try:
            response = await call_next(request)
        except Exception:
            log.exception("unhandled error", extra={"path": request.url.path})
            response = JSONResponse(
                {"detail": "Something went wrong on our side. Try again shortly.", "request_id": rid}, 500
            )
        duration = round((time.perf_counter() - start) * 1000, 1)
        response.headers["X-Request-ID"] = rid
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["Referrer-Policy"] = "no-referrer"
        response.headers["X-Frame-Options"] = "DENY"
        log.info(
            "request",
            extra={
                "path": request.url.path,
                "status": response.status_code,
                "duration_ms": duration,
                "user_id": getattr(request.state, "user_id", None),
            },
        )
        request_id.reset(token)
        return response

    @app.get("/health")
    def health() -> dict:
        return {"status": "ok"}

    @app.get("/ready")
    def ready() -> JSONResponse:
        checks = {
            "database": False,
            "llm_configured": bool(settings.gemini_api_key),
            "search_configured": bool(settings.tavily_api_key),
        }
        try:
            with get_engine().connect() as conn:
                conn.execute(text("SELECT 1"))
            checks["database"] = True
        except Exception:
            log.exception("readiness check failed")
        ok = all(checks.values())
        return JSONResponse({"ready": ok, "checks": checks}, status_code=200 if ok else 503)

    @app.get("/legal/versions")
    def legal_versions() -> dict:
        return {"terms": settings.terms_version, "privacy": settings.privacy_version}

    for r in (
        account.router,
        workspaces.router,
        runs.router,
        documents.router,
        decision.router,
        evidence.router,
        share.router,
        growth.router,
        share.public,
    ):
        app.include_router(r)
    return app


app = create_app()
