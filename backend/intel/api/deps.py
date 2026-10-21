from fastapi import Depends, Request
from sqlalchemy.orm import Session

from intel.config import Settings, get_settings
from intel.models import AuditLog
from intel.security.ratelimit import TokenBucketLimiter

_limiters: dict[str, TokenBucketLimiter] = {}


def limiter(name: str, per_minute: int) -> TokenBucketLimiter:
    if name not in _limiters:
        _limiters[name] = TokenBucketLimiter(per_minute)
    return _limiters[name]


def rate_limited(request: Request, settings: Settings = Depends(get_settings)) -> None:
    limiter("default", settings.rate_limit_per_minute).check(request)


def expensive(request: Request) -> None:
    """Planning, uploads and exports cost money or CPU; allow a handful per minute."""
    limiter("expensive", 6).check(request)


def audit(db: Session, action: str, user_id: str | None, workspace_id: str | None = None, **detail) -> None:
    db.add(AuditLog(action=action, user_id=user_id, workspace_id=workspace_id, detail=detail))
