from fastapi import APIRouter, Depends, HTTPException

import database as db
from auth import get_business_id
from models.admin import (
    InsertMenuPageRequest,
    InsertUserAuthorizationRequest,
    UpdateMenuPageRequest,
    UpdateMetalRatesRequest,
    UpdateUserAuthorizationRequest,
)

router = APIRouter(prefix="/api/admin", tags=["Admin"])


# ── User Authorization ────────────────────────────────────────────────────────

@router.get("/getUserAuthorizations")
def get_all_user_authorizations(business_id: int = Depends(get_business_id)):
    try:
        return db.get_all_user_authorizations(business_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/insertUserAuthorization")
def insert_user_authorization(body: InsertUserAuthorizationRequest, business_id: int = Depends(get_business_id)):
    try:
        db.insert_user_authorization(business_id, body.user_id, body.page_name, body.can_access)
        return {"status": "ok"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/updateUserAuthorization")
def update_user_authorization(body: UpdateUserAuthorizationRequest, business_id: int = Depends(get_business_id)):
    try:
        db.update_user_authorization(business_id, body.id, body.user_id, body.page_name, body.can_access)
        return {"status": "ok"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/deleteUserAuthorization")
def delete_user_authorization(id: int, business_id: int = Depends(get_business_id)):
    try:
        db.delete_user_authorization(business_id, id)
        return {"status": "ok"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ── Menu Pages ────────────────────────────────────────────────────────────────

@router.get("/getMenuPages")
def get_all_menu_pages(business_id: int = Depends(get_business_id)):
    try:
        return db.get_all_menu_pages(business_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/insertMenuPage")
def insert_menu_page(body: InsertMenuPageRequest, business_id: int = Depends(get_business_id)):
    try:
        db.insert_menu_page(
            business_id, body.page_url, body.display_name, body.sort_order,
            body.is_active, body.category, body.category_icon,
            body.page_icon, body.category_order, body.app_version,
        )
        return {"status": "ok"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/updateMenuPage")
def update_menu_page(body: UpdateMenuPageRequest, business_id: int = Depends(get_business_id)):
    try:
        db.update_menu_page(
            business_id, body.menu_id, body.page_url, body.display_name, body.sort_order,
            body.is_active, body.category, body.category_icon,
            body.page_icon, body.category_order, body.app_version,
        )
        return {"status": "ok"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/deleteMenuPage")
def delete_menu_page(menuId: int, business_id: int = Depends(get_business_id)):
    try:
        db.delete_menu_page(business_id, menuId)
        return {"status": "ok"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ── Metal Rates ───────────────────────────────────────────────────────────────

@router.post("/updateMetalRates")
def update_metal_rates(body: UpdateMetalRatesRequest, business_id: int = Depends(get_business_id)):
    try:
        db.update_metal_rates(business_id, body.gold_rate, body.silver_rate, body.created_by)
        return {"status": "ok"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/getLatestMetalRates")
def get_latest_metal_rates(business_id: int = Depends(get_business_id)):
    try:
        return db.get_latest_metal_rates(business_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
