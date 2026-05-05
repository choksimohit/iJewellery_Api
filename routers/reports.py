import json
import time

from fastapi import APIRouter, HTTPException, Request

import database as db
from auth import get_business_id_optional

router = APIRouter(prefix="/api/reports", tags=["Reports"])


async def _run(business_id: int, request: Request, url: str, req_body: dict, fn, *args):
    start = time.time()
    try:
        result = fn(*args)
        elapsed = int((time.time() - start) * 1000)
        await db.log_api_call(
            business_id=business_id, method="GET", url=url,
            request_body=json.dumps(req_body, default=str),
            response_body=json.dumps(result, default=str),
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
            request_body=json.dumps(req_body, default=str),
            response_body=str(e), status_code=500, execution_time_ms=elapsed,
            user_agent=request.headers.get("user-agent", ""),
            client_ip=request.client.host if request.client else "",
            exception=str(e),
        )
        raise HTTPException(status_code=500, detail="An error occurred.")


@router.get("/getInterestEarned")
async def get_interest_earned(request: Request):
    business_id = get_business_id_optional(request)
    return await _run(business_id, request, "getInterestEarned", {},
                      db.get_interest_earned, business_id)


@router.get("/getDailyTransaction")
async def get_daily_transaction(request: Request):
    business_id = get_business_id_optional(request)
    return await _run(business_id, request, "getDailyTransaction", {},
                      db.get_daily_transaction, business_id)


@router.get("/getLoanTransactions")
async def get_loan_transactions(loanNumber: int, request: Request):
    business_id = get_business_id_optional(request)
    return await _run(business_id, request, "getLoanTransactions", {"loanNumber": loanNumber},
                      db.get_loan_transactions, business_id, loanNumber)


@router.get("/getLoanSourceWiseAmountTotal")
async def get_loan_source_wise_total(request: Request):
    business_id = get_business_id_optional(request)
    return await _run(business_id, request, "getLoanSourceWiseAmountTotal", {},
                      db.get_loan_source_wise_total, business_id)
