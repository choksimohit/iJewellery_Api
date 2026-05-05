import json
import time

from fastapi import APIRouter, HTTPException, Request

import database as db
from auth import get_business_id_optional

router = APIRouter(prefix="/api/masterData", tags=["Master Data"])


async def _run(business_id: int, request: Request, url: str, fn, *args):
    start = time.time()
    try:
        result = fn(*args)
        elapsed = int((time.time() - start) * 1000)
        await db.log_api_call(
            business_id=business_id, method="GET", url=url,
            request_body="", response_body=json.dumps(result, default=str),
            status_code=200, execution_time_ms=elapsed,
            user_agent=request.headers.get("user-agent", ""),
            client_ip=request.client.host if request.client else "",
            exception="Success.",
        )
        return result
    except Exception as e:
        elapsed = int((time.time() - start) * 1000)
        await db.log_api_call(
            business_id=business_id, method="GET", url=url,
            request_body="", response_body=str(e), status_code=500,
            execution_time_ms=elapsed,
            user_agent=request.headers.get("user-agent", ""),
            client_ip=request.client.host if request.client else "",
            exception=str(e),
        )
        raise HTTPException(status_code=500, detail="An error occurred.")


@router.get("/getAllVillages")
async def get_all_villages(request: Request):
    business_id = get_business_id_optional(request)
    return await _run(business_id, request, "getAllVillages", db.get_all_villages, business_id)


@router.get("/getAllItemTypes")
async def get_all_item_types(request: Request):
    business_id = get_business_id_optional(request)
    return await _run(business_id, request, "getAllItemTypes", db.get_all_item_types, business_id)


@router.get("/getAllMetalTypes")
async def get_all_metal_types(request: Request):
    business_id = get_business_id_optional(request)
    return await _run(business_id, request, "getAllMetalTypes", db.get_all_metal_types, business_id)


@router.get("/getAllLoanSources")
async def get_all_loan_sources(request: Request):
    business_id = get_business_id_optional(request)
    return await _run(business_id, request, "getAllLoanSources", db.get_all_loan_sources, business_id)


@router.get("/getAllLoanSourceUpdateLogs")
async def get_all_loan_source_update_logs(request: Request):
    business_id = get_business_id_optional(request)
    return await _run(business_id, request, "getAllLoanSourceUpdateLogs",
                      db.get_all_loan_source_update_logs, business_id)
