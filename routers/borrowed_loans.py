from fastapi import APIRouter, Depends, HTTPException

import database as db
from auth import get_business_id
from models.borrowed_loan import (
    CloseBorrowedLoanRequest,
    DeleteBorrowedLoanRequest,
    InsertBorrowedLoanRequest,
    UpdateBorrowedLoanRequest,
)

router = APIRouter(prefix="/api/borrowedLoans", tags=["Borrowed Loans"])


@router.get("/getAll")
def get_all_borrowed_loans(filterStatus: str = "ALL", business_id: int = Depends(get_business_id)):
    try:
        return db.get_all_borrowed_loans(business_id, filterStatus)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/getById")
def get_borrowed_loan_by_id(borrowedLoanId: int, business_id: int = Depends(get_business_id)):
    try:
        return db.get_borrowed_loan_by_id(business_id, borrowedLoanId)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/insert")
def insert_borrowed_loan(body: InsertBorrowedLoanRequest, business_id: int = Depends(get_business_id)):
    try:
        new_id = db.insert_borrowed_loan(
            business_id, body.borrowing_date, body.party_name, body.party_contact,
            body.party_address, body.principal_amount, body.interest_rate,
            body.interest_type, body.due_date, body.notes, body.created_by,
        )
        return {"BorrowedLoanID": new_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/update")
def update_borrowed_loan(body: UpdateBorrowedLoanRequest, business_id: int = Depends(get_business_id)):
    try:
        db.update_borrowed_loan(
            business_id, body.borrowed_loan_id, body.borrowing_date, body.party_name,
            body.party_contact, body.party_address, body.principal_amount,
            body.interest_rate, body.interest_type, body.due_date, body.notes, body.updated_by,
        )
        return {"status": "ok"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/close")
def close_borrowed_loan(body: CloseBorrowedLoanRequest, business_id: int = Depends(get_business_id)):
    try:
        db.close_borrowed_loan(
            business_id, body.borrowed_loan_id, body.closure_date,
            body.closure_amount, body.closure_notes, body.closed_by,
        )
        return {"status": "ok"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/delete")
def delete_borrowed_loan(body: DeleteBorrowedLoanRequest, business_id: int = Depends(get_business_id)):
    try:
        db.delete_borrowed_loan(business_id, body.borrowed_loan_id, body.deleted_by)
        return {"status": "ok"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
