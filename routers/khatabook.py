from fastapi import APIRouter, Depends, HTTPException

import database as db
from auth import get_business_id
from models.khatabook import (
    KhataAddBillRequest,
    KhataAddTransactionRequest,
    KhataDeleteBillRequest,
    KhataDeleteTransactionRequest,
)

router = APIRouter(prefix="/api/khatabook", tags=["Khatabook"])


@router.post("/addBill")
def khata_add_bill(body: KhataAddBillRequest, business_id: int = Depends(get_business_id)):
    try:
        bill_id = db.khata_add_bill(
            business_id, body.customer_id, body.bill_no,
            body.bill_date, body.amount, body.notes, body.created_by,
        )
        return {"BillID": bill_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/addDebitToBill")
def khata_add_debit_to_bill(body: KhataAddTransactionRequest, business_id: int = Depends(get_business_id)):
    try:
        db.khata_add_debit_to_bill(
            business_id, body.bill_id, body.txn_date, body.amount, body.notes, body.created_by,
        )
        return {"status": "ok"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/addPayment")
def khata_add_payment(body: KhataAddTransactionRequest, business_id: int = Depends(get_business_id)):
    try:
        db.khata_add_payment(
            business_id, body.bill_id, body.txn_date, body.amount, body.notes, body.created_by,
        )
        return {"status": "ok"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/getCustomerBalances")
def khata_get_customer_balances(showAll: bool = False, business_id: int = Depends(get_business_id)):
    try:
        return db.khata_get_customer_balances(business_id, showAll)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/getCustomerBills")
def khata_get_customer_bills(customerId: int, business_id: int = Depends(get_business_id)):
    try:
        return db.khata_get_customer_bills(business_id, customerId)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/getAllBillTransactions")
def khata_get_all_bill_transactions(customerId: int, business_id: int = Depends(get_business_id)):
    try:
        return db.khata_get_all_bill_transactions(business_id, customerId)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/getOpenBillsForPayment")
def khata_get_open_bills_for_payment(customerId: int, business_id: int = Depends(get_business_id)):
    try:
        return db.khata_get_open_bills_for_payment(business_id, customerId)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/deleteTransaction")
def khata_delete_transaction(body: KhataDeleteTransactionRequest, business_id: int = Depends(get_business_id)):
    try:
        db.khata_delete_transaction(business_id, body.txn_id, body.deleted_by)
        return {"status": "ok"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/deleteBill")
def khata_delete_bill(body: KhataDeleteBillRequest, business_id: int = Depends(get_business_id)):
    try:
        db.khata_delete_bill(business_id, body.bill_id, body.deleted_by)
        return {"status": "ok"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
