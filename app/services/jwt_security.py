from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

import bcrypt
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.config import settings

oauth2_scheme = HTTPBearer(auto_error=False)


def _read_key(path: str | Path) -> str:
    return Path(path).read_text(encoding="utf-8")


def encode_jwt(
    payload: dict[str, Any],
    *,
    private_key: str | None = None,
    algorithm: str | None = None,
    expire_minutes: int | None = None,
) -> str:
    private_key = private_key or _read_key(settings.jwt.JWT_PRIVATE_KEY_PATH)
    algorithm = algorithm or settings.jwt.JWT_ALGORITHM

    to_encode = payload.copy()
    now = datetime.now(timezone.utc)

    if expire_minutes is not None:
        to_encode.update(
            exp=now + timedelta(minutes=expire_minutes),
            iat=now,
        )

    return jwt.encode(to_encode, private_key, algorithm=algorithm)


def decode_jwt(
    token: str | bytes,
    *,
    public_key: str | None = None,
    algorithm: str | None = None,
) -> dict[str, Any]:
    public_key = public_key or _read_key(settings.jwt.JWT_PUBLIC_KEY_PATH)
    algorithm = algorithm or settings.jwt.JWT_ALGORITHM

    return jwt.decode(token, public_key, algorithms=[algorithm])


def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
    return hashed.decode("utf-8")


def validate_password(password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(
        password=password.encode("utf-8"),
        hashed_password=hashed_password.encode("utf-8"),
    )


def create_jwt(
    *,
    token_type: str,
    token_data: dict[str, Any],
    expire_minutes: int,
) -> str:
    jwt_payload = {"type": token_type}
    jwt_payload.update(token_data)

    return encode_jwt(
        payload=jwt_payload,
        expire_minutes=expire_minutes,
    )


def create_access_token(token_data: dict[str, Any]) -> str:
    return create_jwt(
        token_type="access",
        token_data=token_data,
        expire_minutes=settings.jwt.ACCESS_TOKEN_EXPIRE_MINUTES,
    )


def create_refresh_token(token_data: dict[str, Any]) -> str:
    return create_jwt(
        token_type="refresh",
        token_data=token_data,
        expire_minutes=settings.jwt.REFRESH_TOKEN_EXPIRE_MINUTES,
    )


def extract_bearer_token(
    credentials: HTTPAuthorizationCredentials = Depends(oauth2_scheme),
) -> str:
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authorization token",
        )

    if credentials.scheme.lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization scheme",
        )

    return credentials.credentials