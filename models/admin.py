from typing import Optional
from pydantic import BaseModel


class InsertUserAuthorizationRequest(BaseModel):
    user_id: int
    page_name: str
    can_access: bool


class UpdateUserAuthorizationRequest(BaseModel):
    id: int
    user_id: int
    page_name: str
    can_access: bool


class InsertMenuPageRequest(BaseModel):
    page_url: str
    display_name: str
    sort_order: int
    is_active: bool
    category: Optional[str] = None
    category_icon: Optional[str] = None
    page_icon: Optional[str] = None
    category_order: Optional[int] = None
    app_version: Optional[str] = None


class UpdateMenuPageRequest(InsertMenuPageRequest):
    menu_id: int


class UpdateMetalRatesRequest(BaseModel):
    gold_rate: float
    silver_rate: float
    created_by: str
