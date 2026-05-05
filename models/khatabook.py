from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class KhataAddBillRequest(BaseModel):
    customer_id: int
    bill_no: str
    bill_date: datetime
    amount: float
    notes: Optional[str] = None
    created_by: str


class KhataAddTransactionRequest(BaseModel):
    bill_id: int
    txn_date: datetime
    amount: float
    notes: Optional[str] = None
    created_by: str


class KhataDeleteTransactionRequest(BaseModel):
    txn_id: int
    deleted_by: str


class KhataDeleteBillRequest(BaseModel):
    bill_id: int
    deleted_by: str
