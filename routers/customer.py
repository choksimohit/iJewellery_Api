from fastapi import APIRouter, HTTPException

import database as db
from models.customer import InsertCustomerLedgerRequest, UpsertCustomerRequest

router = APIRouter(prefix="/api/customer", tags=["Customer"])


@router.post("/upsertCustomer")
def upsert_customer(body: UpsertCustomerRequest, business_id: int = 1):
    try:
        result = db.upsert_customer(
            business_id,
            body.cust_id, body.customer_name, body.care_of_customer_name,
            body.phone, body.address_line1, body.address_line2,
            body.village, body.created_by, body.is_update,
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/getCustomersByMobile")
def get_customers_by_mobile(mobile: str, business_id: int = 1):
    try:
        return db.get_customers_by_mobile(business_id, mobile)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/getCustomersById")
def get_customers_by_id(custId: int, business_id: int = 1):
    try:
        return db.get_customers_by_id(business_id, custId)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/getCustomersByName")
def get_customers_by_name(name: str, business_id: int = 1):
    try:
        return db.get_customers_by_name(business_id, name)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/getCustomersByAddress")
def get_customers_by_address(address: str, business_id: int = 1):
    try:
        return db.get_customers_by_address(business_id, address)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/insertCustomerLedger")
def insert_customer_ledger(body: InsertCustomerLedgerRequest, business_id: int = 1):
    try:
        result = db.insert_customer_ledger(
            business_id,
            body.customer_id, body.ledger_date, body.credit,
            body.debit, body.invoice_no, body.description, body.created_by,
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/getCustomerLedger")
def get_customer_ledger(customerId: int, business_id: int = 1):
    try:
        return db.get_customer_ledger(business_id, customerId)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
