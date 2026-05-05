from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt

from config import settings

_bearer = HTTPBearer()


def create_access_token(username: str, business_id: int, expires_hours: int = 24) -> str:
    expire = datetime.now(timezone.utc) + timedelta(hours=expires_hours)
    payload = {
        "sub": username,
        "BusinessId": str(business_id),
        "exp": expire,
    }
    return jwt.encode(payload, settings.jwt_key, algorithm="HS256")


def decode_token(token: str) -> dict:
    try:
        return jwt.decode(
            token,
            settings.jwt_key,
            algorithms=["HS256"],
            options={"verify_aud": False, "verify_iss": False},
        )
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        ) from e


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(_bearer)) -> dict:
    return decode_token(credentials.credentials)


def get_business_id(current_user: dict = Depends(get_current_user)) -> int:
    business_id = current_user.get("BusinessId")
    if business_id is None:
        raise HTTPException(status_code=400, detail="BusinessId claim missing from token")
    return int(business_id)


def get_business_id_optional(request: Request) -> int:
    """For public endpoints — defaults to business 1 if no token present."""
    auth_header = request.headers.get("Authorization", "")
    if auth_header.startswith("Bearer "):
        token = auth_header.split(" ", 1)[1]
        try:
            payload = decode_token(token)
            return int(payload.get("BusinessId", 1))
        except HTTPException:
            pass
    return 1
