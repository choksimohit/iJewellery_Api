from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class InsertBorrowedLoanRequest(BaseModel):
    borrowing_date: datetime
    party_name: str
    party_contact: Optional[str] = None
    party_address: Optional[str] = None
    principal_amount: float
    interest_rate: float
    interest_type: str
    due_date: Optional[datetime] = None
    notes: Optional[str] = None
    created_by: str


class UpdateBorrowedLoanRequest(BaseModel):
    borrowed_loan_id: int
    borrowing_date: datetime
    party_name: str
    party_contact: Optional[str] = None
    party_address: Optional[str] = None
    principal_amount: float
    interest_rate: float
    interest_type: str
    due_date: Optional[datetime] = None
    notes: Optional[str] = None
    updated_by: str


class CloseBorrowedLoanRequest(BaseModel):
    borrowed_loan_id: int
    closure_date: datetime
    closure_amount: float
    closure_notes: Optional[str] = None
    closed_by: str


class DeleteBorrowedLoanRequest(BaseModel):
    borrowed_loan_id: int
    deleted_by: str
