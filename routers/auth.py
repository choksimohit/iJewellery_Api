import json
import time

from fastapi import APIRouter, HTTPException, Request, status

import database as db
from auth import create_access_token, get_business_id_optional
from models.auth import LoginRequest

router = APIRouter(prefix="/api/auth", tags=["Auth"])


@router.post("/login")
def login(request_body: LoginRequest):
    """Authenticate user and return a JWT token."""
    valid = db.validate_user(request_body.business_id, request_body.username, request_body.password)
    if not valid:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    token = create_access_token(request_body.username, request_body.business_id)
    return {"access_token": token, "token_type": "bearer"}


@router.get("/getUserAuthenticationAll")
def get_user_authentication_all(pageURL: str, UserId: str, request: Request):
    business_id = get_business_id_optional(request)
    start = time.time()
    try:
        result = db.get_user_authentication_all(business_id, pageURL, UserId)
        return result
    except Exception as e:
        elapsed = int((time.time() - start) * 1000)
        db_args = dict(
            business_id=business_id, method="GET", url="getUserAuthenticationAll",
            request_body=json.dumps({"pageURL": pageURL, "UserId": UserId}),
            response_body=str(e), status_code=500, execution_time_ms=elapsed,
            user_agent=request.headers.get("user-agent", ""),
            client_ip=request.client.host if request.client else "",
            exception=str(e),
        )
        import asyncio
        asyncio.create_task(db.log_api_call(**db_args))
        raise HTTPException(status_code=500, detail="An error occurred.")
