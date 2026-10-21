"""Bearer-token authentication.

Production verifies Supabase-issued JWTs: HS256 with the project's JWT secret, or asymmetric
keys from the project's JWKS endpoint. Development mode accepts HS256 tokens signed with
DEV_JWT_SECRET so the app can run without a Supabase project; it is refused in production.
"""

from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from functools import lru_cache

import jwt
from fastapi import Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from intel.config import Settings, get_settings
from intel.db import get_db
from intel.models import Membership, User

ROLE_RANK = {"viewer": 0, "editor": 1, "owner": 2}


@dataclass(frozen=True)
class Principal:
    user_id: str
    email: str | None


def _unauthorized(detail: str = "Sign in to continue.") -> HTTPException:
    return HTTPException(status.HTTP_401_UNAUTHORIZED, detail, headers={"WWW-Authenticate": "Bearer"})


@lru_cache
def _jwks_client(url: str) -> jwt.PyJWKClient:
    return jwt.PyJWKClient(url, cache_keys=True)


def decode_token(token: str, settings: Settings) -> Principal:
    try:
        if settings.auth_mode == "dev":
            if settings.environment == "production":
                raise _unauthorized("Development sign-in is disabled in production.")
            claims = jwt.decode(token, settings.dev_jwt_secret, algorithms=["HS256"], audience="authenticated")
        else:
            header = jwt.get_unverified_header(token)
            if header.get("alg") == "HS256":
                if not settings.supabase_jwt_secret:
                    raise _unauthorized("Server is missing SUPABASE_JWT_SECRET.")
                key: object = settings.supabase_jwt_secret
                algorithms = ["HS256"]
            else:
                if not settings.supabase_url:
                    raise _unauthorized("Server is missing SUPABASE_URL.")
                jwks = _jwks_client(f"{settings.supabase_url.rstrip('/')}/auth/v1/.well-known/jwks.json")
                key = jwks.get_signing_key_from_jwt(token).key
                algorithms = ["RS256", "ES256"]
            claims = jwt.decode(
                token,
                key,  # type: ignore[arg-type]
                algorithms=algorithms,
                audience=settings.supabase_jwt_audience,
                issuer=f"{settings.supabase_url.rstrip('/')}/auth/v1" if settings.supabase_url else None,
                options={"verify_iss": bool(settings.supabase_url)},
            )
    except jwt.PyJWTError as exc:
        raise _unauthorized("Your session is invalid or has expired. Sign in again.") from exc
    sub = claims.get("sub")
    if not sub:
        raise _unauthorized()
    return Principal(user_id=str(sub), email=claims.get("email"))


def mint_dev_token(user_id: str, email: str, settings: Settings, hours: int = 12) -> str:
    if settings.auth_mode != "dev" or settings.environment == "production":
        raise RuntimeError("Development tokens are only available in dev auth mode outside production.")
    payload = {
        "sub": user_id,
        "email": email,
        "aud": "authenticated",
        "exp": datetime.now(UTC) + timedelta(hours=hours),
        "iat": datetime.now(UTC),
    }
    return jwt.encode(payload, settings.dev_jwt_secret, algorithm="HS256")


def current_principal(request: Request, settings: Settings = Depends(get_settings)) -> Principal:
    header = request.headers.get("authorization", "")
    if not header.lower().startswith("bearer "):
        raise _unauthorized()
    principal = decode_token(header.split(" ", 1)[1].strip(), settings)
    request.state.user_id = principal.user_id
    return principal


def current_user(principal: Principal = Depends(current_principal), db: Session = Depends(get_db)) -> User:
    user = db.get(User, principal.user_id)
    if user is None:
        user = User(id=principal.user_id, email=principal.email)
        db.add(user)
        db.commit()
    return user


def accepted_user(user: User = Depends(current_user), settings: Settings = Depends(get_settings)) -> User:
    """Users must accept the current terms and privacy notice before using the service."""
    if user.terms_version != settings.terms_version or user.privacy_version != settings.privacy_version:
        raise HTTPException(
            status.HTTP_403_FORBIDDEN, {"code": "terms_required", "terms_version": settings.terms_version}
        )
    return user


def require_role(db: Session, user: User, workspace_id: str, minimum: str) -> Membership:
    m = db.query(Membership).filter_by(workspace_id=workspace_id, user_id=user.id).one_or_none()
    # Not-a-member and missing workspace look the same so IDs can't be probed.
    if m is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Workspace not found.")
    if ROLE_RANK[m.role] < ROLE_RANK[minimum]:
        raise HTTPException(status.HTTP_403_FORBIDDEN, f"This needs the {minimum} role in the workspace.")
    return m
