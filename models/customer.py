from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class UpsertCustomerRequest(BaseModel):
    cust_id: int
    customer_name: str
    care_of_customer_name: str
    phone: int
    address_line1: str
    address_line2: str
    village: str
    created_by: str
    is_update: bool


class InsertCustomerLedgerRequest(BaseModel):
    customer_id: int
    ledger_date: datetime
    credit: float
    debit: float
    invoice_no: str
    description: str
    created_by: str


class InsertCustomerRequest(BaseModel):
    name: str
    address: Optional[str] = None
    created_by: str


class UpdateCustomerRequest(BaseModel):
    customer_id: int
    name: str
    address: Optional[str] = None


class InsertCustomerPhoneRequest(BaseModel):
    customer_id: int
    phone: str
    is_primary: bool
    created_by: str


class MergeCustomersRequest(BaseModel):
    master_id: int
    duplicate_ids: str
