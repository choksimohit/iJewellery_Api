from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from fastapi.responses import Response

import database as db
from auth import get_business_id, get_current_user
from models.customer import (
    InsertCustomerLedgerRequest,
    InsertCustomerPhoneRequest,
    InsertCustomerRequest,
    MergeCustomersRequest,
    UpdateCustomerRequest,
    UpsertCustomerRequest,
)

router = APIRouter(prefix="/api/customer", tags=["Customer"],
                   dependencies=[Depends(get_current_user)])


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


# ── Manage Customer (extended) ────────────────────────────────────────────────

@router.get("/getCustomers")
def get_customers(business_id: int = Depends(get_business_id)):
    try:
        return db.get_customers(business_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/getCustomerById")
def get_customer_by_id(customerId: int, business_id: int = Depends(get_business_id)):
    try:
        return db.get_customer_by_id(business_id, customerId)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/insertCustomer")
def insert_customer(body: InsertCustomerRequest, business_id: int = Depends(get_business_id)):
    try:
        new_id = db.insert_customer(business_id, body.name, body.address, body.created_by)
        return {"CustomerID": new_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/updateCustomer")
def update_customer(body: UpdateCustomerRequest, business_id: int = Depends(get_business_id)):
    try:
        db.update_customer(business_id, body.customer_id, body.name, body.address)
        return {"status": "ok"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/deleteCustomer")
def delete_customer(customerId: int, business_id: int = Depends(get_business_id)):
    try:
        db.delete_customer(business_id, customerId)
        return {"status": "ok"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/getPhonesByCustomer")
def get_phones_by_customer(customerId: int, business_id: int = Depends(get_business_id)):
    try:
        return db.get_phones_by_customer(business_id, customerId)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/insertCustomerPhone")
def insert_customer_phone(body: InsertCustomerPhoneRequest, business_id: int = Depends(get_business_id)):
    try:
        new_id = db.insert_customer_phone(
            business_id, body.customer_id, body.phone, body.is_primary, body.created_by,
        )
        return {"PhoneID": new_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/deleteCustomerPhone")
def delete_customer_phone(phoneId: int, business_id: int = Depends(get_business_id)):
    try:
        db.delete_customer_phone(business_id, phoneId)
        return {"status": "ok"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/setPrimaryPhone")
def set_primary_phone(customerId: int, phoneId: int, business_id: int = Depends(get_business_id)):
    try:
        db.set_primary_phone(business_id, customerId, phoneId)
        return {"status": "ok"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/mergeCustomers")
def merge_customers(body: MergeCustomersRequest, business_id: int = Depends(get_business_id)):
    try:
        return db.merge_customers(business_id, body.master_id, body.duplicate_ids)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ── Entity / Customer Photos ──────────────────────────────────────────────────

@router.post("/updateEntityPhoto")
async def update_entity_photo(
    entity_type: str = Form(...),
    entity_id: int = Form(...),
    updated_by: str = Form(...),
    photo: UploadFile = File(...),
    business_id: int = Depends(get_business_id),
):
    try:
        photo_bytes = await photo.read()
        db.update_entity_photo(business_id, entity_type, entity_id, photo_bytes, photo.content_type, updated_by)
        return {"status": "ok"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/getEntityPhoto")
def get_entity_photo(entityType: str, entityId: int, business_id: int = Depends(get_business_id)):
    try:
        photo_bytes, content_type = db.get_entity_photo(business_id, entityType, entityId)
        if photo_bytes is None:
            raise HTTPException(status_code=404, detail="Photo not found")
        return Response(content=photo_bytes, media_type=content_type)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/updateCustomerPhoto")
async def update_customer_photo(
    customer_id: int = Form(...),
    updated_by: str = Form(...),
    photo: UploadFile = File(...),
    business_id: int = Depends(get_business_id),
):
    try:
        photo_bytes = await photo.read()
        db.update_customer_photo(business_id, customer_id, photo_bytes, photo.content_type, updated_by)
        return {"status": "ok"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/getCustomerPhoto")
def get_customer_photo(customerId: int, business_id: int = Depends(get_business_id)):
    try:
        photo_bytes, content_type = db.get_customer_photo(business_id, customerId)
        if photo_bytes is None:
            raise HTTPException(status_code=404, detail="Photo not found")
        return Response(content=photo_bytes, media_type=content_type)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
