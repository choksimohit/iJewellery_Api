from datetime import datetime
from pydantic import BaseModel


class InsertLoanRequest(BaseModel):
    loan_number: str
    loan_date: datetime
    name: str
    address: str
    phone: str
    metal_type: str
    metal_price: float
    item_type_id: int
    item_weight: float
    item_description: str
    loan_amount: float
    loan_source_id: int
    created_by: str


class UpdateLoanRequest(InsertLoanRequest):
    is_closure: int


class UpdateLoanClosureRequest(BaseModel):
    loan_number: str
    closure_date: datetime
    closure_amount: float
    closure_comments: str
    closure_by: str


class UpdateLoanSourceRequest(BaseModel):
    loan_number: str
    loan_source_update_date: datetime
    new_loan_source_id: int
    new_loan_source_amount: float
    description: str
    created_by: str


class UpdatePartLoanRequest(BaseModel):
    loan_number: str
    new_loan_date: datetime
    net_payable_amount: float
    additional_loan_amount: float
    created_by: str
