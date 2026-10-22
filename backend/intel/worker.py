"""Database-backed job queue. Run `python -m intel.worker`, or let the API start an in-process worker."""

import logging
import threading
import time
from datetime import UTC, datetime, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from intel.config import Settings, get_settings
from intel.db import session_factory
from intel.growth import due_refreshes
from intel.logging_setup import configure_logging
from intel.models import Job, Run, SearchCache
from intel.pipeline.orchestrator import execute_run
from intel.providers import factory
from intel.providers.errors import ProviderError
from intel.providers.search import CACHE_TTL

log = logging.getLogger(__name__)
STALE_AFTER = timedelta(minutes=30)


def claim_next(db: Session) -> Job | None:
    stmt = select(Job).where(Job.status == "queued").order_by(Job.created_at).limit(1)
    if db.bind is not None and db.bind.dialect.name == "postgresql":
        stmt = stmt.with_for_update(skip_locked=True)
    job = db.execute(stmt).scalar_one_or_none()
    if job is None:
        return None
    job.status, job.locked_at, job.attempts = "running", datetime.now(UTC), job.attempts + 1
    db.commit()
    return job


def requeue_stale(db: Session) -> None:
    cutoff = datetime.now(UTC) - STALE_AFTER
    for job in db.query(Job).filter(Job.status == "running").all():
        locked = (
            job.locked_at if job.locked_at and job.locked_at.tzinfo else (job.locked_at or cutoff).replace(tzinfo=UTC)
        )
        if locked < cutoff:
            job.status = "queued" if job.attempts < 2 else "failed"
            job.error = "Worker stopped while running this job."
    db.commit()


def purge_expired(db: Session) -> int:
    """Enforce retention promised in the privacy notice for data the Service caches."""
    cutoff = datetime.now(UTC) - CACHE_TTL
    n = db.query(SearchCache).filter(SearchCache.created_at < cutoff).delete()
    db.commit()
    return n


def process_one(settings: Settings | None = None) -> bool:
    settings = settings or get_settings()
    db = session_factory()()
    try:
        job = claim_next(db)
        if job is None:
            return False
        try:
            providers = factory.get_providers(settings)
        except ProviderError as exc:
            run = db.get(Run, job.run_id)
            if run:
                run.status, run.error = "failed", str(exc)
            job.status, job.error = "failed", str(exc)
            db.commit()
            return True
        execute_run(db, job.run_id, providers, settings)
        run = db.get(Run, job.run_id)
        job.status = "done" if run and run.status == "completed" else "failed"
        job.error = run.error if run else "Run missing"
        db.commit()
        return True
    finally:
        db.close()


def loop(stop: threading.Event, interval: float = 2.0) -> None:
    db = session_factory()()
    try:
        requeue_stale(db)
    finally:
        db.close()
    last_purge = 0.0
    while not stop.is_set():
        if time.monotonic() - last_purge > 3600:
            with session_factory()() as s:
                purge_expired(s)
                try:
                    queued = due_refreshes(s, get_settings())
                    if queued:
                        log.info("monthly refresh queued", extra={"runs": queued})
                except Exception:
                    log.exception("monthly refresh failed")
            last_purge = time.monotonic()
        try:
            worked = process_one()
        except Exception:
            log.exception("worker iteration failed")
            worked = False
        if not worked:
            stop.wait(interval)


def start_in_process() -> threading.Event:
    stop = threading.Event()
    threading.Thread(target=loop, args=(stop,), name="intel-worker", daemon=True).start()
    return stop


if __name__ == "__main__":
    configure_logging()
    log.info("worker started")
    try:
        loop(threading.Event())
    except KeyboardInterrupt:
        time.sleep(0)
