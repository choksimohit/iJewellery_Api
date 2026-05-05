import json
import time

from fastapi import APIRouter, Depends, HTTPException, Request
from datetime import datetime

import database as db
from auth import get_business_id, get_current_user
from models.loan import (
    InsertLoanMultiRequest,
    InsertLoanRequest,
    UpdateLoanClosureRequest,
    UpdateLoanHeaderRequest,
    UpdateLoanRequest,
    UpdateLoanSourceRequest,
    UpdatePartLoanRequest,
)

router = APIRouter(
    prefix="/api/loan",
    tags=["Loan"],
    dependencies=[Depends(get_current_user)],
)


async def _run(business_id: int, request: Request, url: str, method: str,
               req_body: dict, fn, *args):
    start = time.time()
    try:
        result = fn(*args)
        elapsed = int((time.time() - start) * 1000)
        await db.log_api_call(
            business_id=business_id, method=method, url=url,
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
            business_id=business_id, method=method, url=url,
            request_body=json.dumps(req_body, default=str),
            response_body=str(e), status_code=500, execution_time_ms=elapsed,
            user_agent=request.headers.get("user-agent", ""),
            client_ip=request.client.host if request.client else "",
            exception=str(e),
        )
        raise HTTPException(status_code=500, detail="An error occurred.")


@router.post("/insertLoan")
async def insert_loan(body: InsertLoanRequest, request: Request,
                      business_id: int = Depends(get_business_id)):
    return await _run(
        business_id, request, "insertLoan", "POST", body.model_dump(),
        db.insert_loan, business_id,
        body.loan_number, body.loan_date, body.name, body.address, body.phone,
        body.metal_type, body.metal_price, body.item_type_id, body.item_weight,
        body.item_description, body.loan_amount, body.loan_source_id, body.created_by,
        body.melting,
    )


@router.post("/updateLoan")
async def update_loan(body: UpdateLoanRequest, request: Request,
                      business_id: int = Depends(get_business_id)):
    return await _run(
        business_id, request, "updateLoan", "POST", body.model_dump(),
        db.update_loan, business_id,
        body.loan_number, body.loan_date, body.name, body.address, body.phone,
        body.metal_type, body.metal_price, body.item_type_id, body.item_weight,
        body.item_description, body.loan_amount, body.loan_source_id,
        body.is_closure, body.created_by,
    )


@router.delete("/deleteLoan")
async def delete_loan(loanNumber: str, createdBy: str, request: Request,
                      business_id: int = Depends(get_business_id)):
    return await _run(
        business_id, request, "deleteLoan", "DELETE",
        {"loanNumber": loanNumber, "createdBy": createdBy},
        db.delete_loan, business_id, loanNumber, createdBy,
    )


@router.get("/getAllLoans")
async def get_all_loans(loanNumber: int, request: Request,
                        business_id: int = Depends(get_business_id)):
    return await _run(
        business_id, request, "getAllLoans", "GET", {"loanNumber": loanNumber},
        db.get_all_loans, business_id, loanNumber,
    )


@router.get("/getAllLoansByMobile")
async def get_all_loans_by_mobile(mobile: str, request: Request,
                                  business_id: int = Depends(get_business_id)):
    return await _run(
        business_id, request, "getAllLoansByMobile", "GET", {"mobile": mobile},
        db.get_all_loans_by_mobile, business_id, mobile,
    )


@router.get("/getAllLoansByName")
async def get_all_loans_by_name(name: str, request: Request,
                                business_id: int = Depends(get_business_id)):
    return await _run(
        business_id, request, "getAllLoansByName", "GET", {"name": name},
        db.get_all_loans_by_name, business_id, name,
    )


@router.get("/getAllLoansByAddress")
async def get_all_loans_by_address(address: str, request: Request,
                                   business_id: int = Depends(get_business_id)):
    return await _run(
        business_id, request, "getAllLoansByAddress", "GET", {"address": address},
        db.get_all_loans_by_address, business_id, address,
    )


@router.get("/getAllLoansBySource")
async def get_all_loans_by_source(loanSourceId: int, request: Request,
                                  business_id: int = Depends(get_business_id)):
    return await _run(
        business_id, request, "getAllLoansBySource", "GET", {"loanSourceId": loanSourceId},
        db.get_all_loans_by_source, business_id, loanSourceId,
    )


@router.get("/getLoanForClosure")
async def get_loan_for_closure(loanNumber: int, request: Request,
                               business_id: int = Depends(get_business_id)):
    return await _run(
        business_id, request, "getLoanForClosure", "GET", {"loanNumber": loanNumber},
        db.get_loan_for_closure, business_id, loanNumber,
    )


@router.post("/updateLoanClosure")
async def update_loan_closure(body: UpdateLoanClosureRequest, request: Request,
                              business_id: int = Depends(get_business_id)):
    return await _run(
        business_id, request, "updateLoanClosure", "POST", body.model_dump(),
        db.update_loan_closure, business_id,
        body.loan_number, body.closure_date, body.closure_amount,
        body.closure_comments, body.closure_by,
    )


@router.post("/updateLoanSource")
async def update_loan_source(body: UpdateLoanSourceRequest, request: Request,
                             business_id: int = Depends(get_business_id)):
    return await _run(
        business_id, request, "updateLoanSource", "POST", body.model_dump(),
        db.update_loan_source, business_id,
        body.loan_number, body.loan_source_update_date, body.new_loan_source_id,
        body.new_loan_source_amount, body.description, body.created_by,
    )


@router.post("/updatePartLoan")
async def update_part_loan(body: UpdatePartLoanRequest, request: Request,
                           business_id: int = Depends(get_business_id)):
    return await _run(
        business_id, request, "updatePartLoan", "POST", body.model_dump(),
        db.update_part_loan, business_id,
        body.loan_number, body.new_loan_date, body.net_payable_amount,
        body.additional_loan_amount, body.created_by,
    )


@router.get("/getLoanTransactions")
async def get_loan_transactions(loanNumber: int, request: Request,
                                business_id: int = Depends(get_business_id)):
    return await _run(
        business_id, request, "getLoanTransactions", "GET", {"loanNumber": loanNumber},
        db.get_loan_transactions, business_id, loanNumber,
    )


@router.get("/getMissingLoanNumbers")
async def get_missing_loan_numbers(request: Request,
                                   business_id: int = Depends(get_business_id)):
    return await _run(
        business_id, request, "getMissingLoanNumbers", "GET", {},
        db.get_missing_loan_numbers, business_id,
    )


@router.get("/getLoanByLoanAmountGreaterThan")
async def get_loan_by_amount(amount: float, loanSourceId: int, request: Request,
                             business_id: int = Depends(get_business_id)):
    return await _run(
        business_id, request, "getLoanByLoanAmountGreaterThan", "GET",
        {"amount": amount, "loanSourceId": loanSourceId},
        db.get_loan_by_amount_greater_than, business_id, amount, loanSourceId,
    )


@router.get("/getLoanByNameSearchQuery")
async def get_loan_by_name_search(name: str, request: Request,
                                  business_id: int = Depends(get_business_id)):
    return await _run(
        business_id, request, "getLoanByNameSearchQuery", "GET", {"name": name},
        db.get_loan_by_name_search, business_id, name,
    )


@router.get("/getNextLoanNumber")
async def get_next_loan_number(request: Request,
                               business_id: int = Depends(get_business_id)):
    return await _run(
        business_id, request, "getNextLoanNumber", "GET", {},
        db.get_next_loan_number, business_id,
    )


@router.get("/getMonthsBetween")
async def get_months_between(FromDate: datetime, ToDate: datetime, request: Request,
                             business_id: int = Depends(get_business_id)):
    return await _run(
        business_id, request, "getMonthsBetween", "GET",
        {"FromDate": str(FromDate), "ToDate": str(ToDate)},
        db.get_months_between, business_id, FromDate, ToDate,
    )


@router.post("/updateLoanHeader")
async def update_loan_header(body: UpdateLoanHeaderRequest, request: Request,
                             business_id: int = Depends(get_business_id)):
    return await _run(
        business_id, request, "updateLoanHeader", "POST", body.model_dump(),
        db.update_loan_header, business_id,
        body.loan_number, body.loan_date, body.loan_amount, body.updated_by,
    )


@router.post("/insertLoanMulti")
async def insert_loan_multi(body: InsertLoanMultiRequest, request: Request,
                            business_id: int = Depends(get_business_id)):
    try:
        conn = db.get_connection(business_id)
        conn.autocommit = False
        try:
            db.insert_loan_multi(
                conn, body.loan_number, body.loan_date, body.name, body.address,
                body.phone, body.loan_amount, body.loan_source_id,
                body.created_by, body.customer_id,
            )
            for item in body.items:
                db.insert_loan_item_multi(
                    conn, body.loan_number, item.metal_type, item.metal_price,
                    item.item_type_id, item.item_weight, item.item_description,
                    item.melting, body.created_by,
                )
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()
        return {"status": "ok", "loan_number": body.loan_number}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
