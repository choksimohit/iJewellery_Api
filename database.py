import hashlib
import time
from datetime import datetime
from typing import Any

import pyodbc

from config import settings


def _get_connection(business_id: int) -> pyodbc.Connection:
    db_name = settings.business_databases.get(business_id)
    if not db_name:
        raise Exception(f"No database configured for BusinessId {business_id}")
    conn_str = (
        f"DRIVER={{ODBC Driver 17 for SQL Server}};"
        f"SERVER={settings.server_name};"
        f"DATABASE={db_name};"
        f"UID={settings.db_username};"
        f"PWD={settings.db_password};"
        f"TrustServerCertificate=yes;"
    )
    return pyodbc.connect(conn_str)


def _rows_to_list(cursor: pyodbc.Cursor) -> list[dict]:
    if cursor.description is None:
        return []
    columns = [col[0] for col in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]


def _call_sp(conn: pyodbc.Connection, sp_name: str, params: list = None) -> list[dict]:
    cursor = conn.cursor()
    if params:
        placeholders = ",".join(["?" for _ in params])
        cursor.execute(f"EXEC {sp_name} {placeholders}", params)
    else:
        cursor.execute(f"EXEC {sp_name}")
    return _rows_to_list(cursor)


# ---------- Connection dependency ----------

def get_connection(business_id: int) -> pyodbc.Connection:
    return _get_connection(business_id)


# ---------- Auth ----------

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def validate_user(business_id: int, username: str, password: str) -> bool:
    hashed = hash_password(password)
    conn = _get_connection(business_id)
    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT COUNT(1) FROM mchoksi.Users WHERE UserName=? AND PasswordHash=?",
            username, hashed,
        )
        return cursor.fetchone()[0] > 0
    finally:
        conn.close()


def get_user_authentication_all(business_id: int, page_url: str, user_id: str) -> list[dict]:
    conn = _get_connection(business_id)
    try:
        return _call_sp(conn, "iJewellery_Get_UserAuthentication", [page_url, user_id])
    finally:
        conn.close()


# ---------- User Authorization CRUD ----------

def get_all_user_authorizations(business_id: int) -> list[dict]:
    conn = _get_connection(business_id)
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM mchoksi.UserAuthorization ORDER BY UserID, PageName")
        return _rows_to_list(cursor)
    finally:
        conn.close()


def insert_user_authorization(business_id: int, user_id: int, page_name: str, can_access: bool) -> None:
    conn = _get_connection(business_id)
    try:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO mchoksi.UserAuthorization (UserID, PageName, CanAccess, CreatedWhen)"
            " VALUES (?, ?, ?, GETDATE())",
            user_id, page_name, can_access,
        )
        conn.commit()
    finally:
        conn.close()


def update_user_authorization(business_id: int, id: int, user_id: int, page_name: str, can_access: bool) -> None:
    conn = _get_connection(business_id)
    try:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE mchoksi.UserAuthorization SET UserID=?, PageName=?, CanAccess=? WHERE ID=?",
            user_id, page_name, can_access, id,
        )
        conn.commit()
    finally:
        conn.close()


def delete_user_authorization(business_id: int, id: int) -> None:
    conn = _get_connection(business_id)
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM mchoksi.UserAuthorization WHERE ID=?", id)
        conn.commit()
    finally:
        conn.close()


# ---------- Admin Menu Page CRUD ----------

def get_all_menu_pages(business_id: int) -> list[dict]:
    conn = _get_connection(business_id)
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM mchoksi.MenuPages ORDER BY CategoryOrder, SortOrder")
        return _rows_to_list(cursor)
    finally:
        conn.close()


def insert_menu_page(business_id: int, page_url: str, display_name: str, sort_order: int,
                     is_active: bool, category: str, category_icon: str, page_icon: str,
                     category_order: int, app_version: str = None) -> None:
    conn = _get_connection(business_id)
    try:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO mchoksi.MenuPages"
            " (PageURL, PageDisplayName, SortOrder, IsActive, Category, CategoryIcon, PageIcon, CategoryOrder, AppVersion)"
            " VALUES (?,?,?,?,?,?,?,?,?)",
            page_url, display_name, sort_order, is_active,
            category, category_icon, page_icon, category_order, app_version,
        )
        conn.commit()
    finally:
        conn.close()


def update_menu_page(business_id: int, menu_id: int, page_url: str, display_name: str,
                     sort_order: int, is_active: bool, category: str, category_icon: str,
                     page_icon: str, category_order: int, app_version: str = None) -> None:
    conn = _get_connection(business_id)
    try:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE mchoksi.MenuPages"
            " SET PageURL=?, PageDisplayName=?, SortOrder=?, IsActive=?,"
            "     Category=?, CategoryIcon=?, PageIcon=?, CategoryOrder=?, AppVersion=?"
            " WHERE MenuID=?",
            page_url, display_name, sort_order, is_active,
            category, category_icon, page_icon, category_order, app_version, menu_id,
        )
        conn.commit()
    finally:
        conn.close()


def delete_menu_page(business_id: int, menu_id: int) -> None:
    conn = _get_connection(business_id)
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM mchoksi.MenuPages WHERE MenuID=?", menu_id)
        conn.commit()
    finally:
        conn.close()


# ---------- Menu ----------

def load_menu_pages(business_id: int, user_name: str, app_version: str = None) -> list[dict]:
    try:
        conn = _get_connection(business_id)
        try:
            return _call_sp(conn, "iJewellery_Get_SidebarMenu", [user_name, app_version])
        finally:
            conn.close()
    except Exception:
        return []


# ---------- Loan ----------

def get_all_loans(business_id: int, loan_number: int) -> list[dict]:
    conn = _get_connection(business_id)
    try:
        return _call_sp(conn, "ijewellery_GET_ALL_LOANS", [loan_number])
    finally:
        conn.close()


def get_all_loans_by_mobile(business_id: int, mobile: str) -> list[dict]:
    conn = _get_connection(business_id)
    try:
        return _call_sp(conn, "iJewellery_Get_All_Loans_FromMobile", [mobile])
    finally:
        conn.close()


def get_all_loans_by_name(business_id: int, name: str) -> list[dict]:
    conn = _get_connection(business_id)
    try:
        return _call_sp(conn, "iJewellery_Get_All_Loans_ByName", [name])
    finally:
        conn.close()


def get_all_loans_by_address(business_id: int, address: str) -> list[dict]:
    conn = _get_connection(business_id)
    try:
        return _call_sp(conn, "iJewellery_Get_All_Loans_ByAddress", [address])
    finally:
        conn.close()


def get_all_loans_by_source(business_id: int, loan_source_id: int) -> list[dict]:
    conn = _get_connection(business_id)
    try:
        return _call_sp(conn, "iJewellery_Get_All_Loans_BySource", [loan_source_id])
    finally:
        conn.close()


def get_loan_for_closure(business_id: int, loan_number: int) -> list[dict]:
    conn = _get_connection(business_id)
    try:
        return _call_sp(conn, "iJewellery_Get_Loan_For_Closure", [loan_number])
    finally:
        conn.close()


def get_loan_transactions(business_id: int, loan_number: int) -> list[dict]:
    conn = _get_connection(business_id)
    try:
        return _call_sp(conn, "iJewellery_GET_LoanTransactions", [loan_number])
    finally:
        conn.close()


def get_missing_loan_numbers(business_id: int) -> list[dict]:
    conn = _get_connection(business_id)
    try:
        return _call_sp(conn, "iJewellery_GET_MISSING_LOANS_ENTRY")
    finally:
        conn.close()


def get_next_loan_number(business_id: int) -> int:
    conn = _get_connection(business_id)
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT ISNULL(Max(LoanNumber),0) from mchoksi.m_Loans")
        return int(cursor.fetchone()[0]) + 1
    finally:
        conn.close()


def get_months_between(business_id: int, from_date: datetime, to_date: datetime) -> int:
    conn = _get_connection(business_id)
    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT dbo.[iJewellery_Get_Months_BetWeen](?,?)",
            from_date.strftime("%Y-%m-%d %H:%M:%S"),
            to_date.strftime("%Y-%m-%d %H:%M:%S"),
        )
        return int(cursor.fetchone()[0])
    finally:
        conn.close()


def get_loan_by_name_search(business_id: int, name: str) -> list[dict]:
    conn = _get_connection(business_id)
    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT [LoanNumber],CONVERT(VARCHAR,[LoanDate]) [LoanDate],[Name],[Address],[Phone],"
            "[MetalType],[ItemName],[MetalWeight],[LoanAmount],"
            "Convert(nvarchar, mchoksi.fnNumberToWordsG(LoanAmount))+N' પુરા' LoanAmountInWords,"
            "[SourceName],CONVERT(VARCHAR,ClosureDate) ClosureDate,[ClosureAmount],[ClosureMonths],"
            "[IsClosure],[LoanSourceID],ItemDescription "
            "FROM mchoksi.Loans WHERE Name Like N'%'+?+'%' ORDER BY LoanNumber DESC",
            name,
        )
        return _rows_to_list(cursor)
    finally:
        conn.close()


def get_loan_by_amount_greater_than(business_id: int, amount: float, loan_source_id: int) -> list[dict]:
    conn = _get_connection(business_id)
    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT [LoanNumber],[LoanDate],[Name],[Address],[Phone],[MetalType],[ItemName],[MetalWeight],"
            "[LoanAmount],[SourceName],[ClosureAmount],[ClosureMonths] LoanTenure,[IsClosure],[LoanSourceID],ItemDescription "
            "FROM mchoksi.Loans WHERE IsClosure=0 AND LoanAmount>=? AND LoanSourceID=? ORDER BY LoanAmount DESC",
            amount, loan_source_id,
        )
        return _rows_to_list(cursor)
    finally:
        conn.close()


def insert_loan(business_id: int, loan_number: str, loan_date: datetime, name: str, address: str,
                phone: str, metal_type: str, metal_price: float, item_type_id: int,
                item_weight: float, item_description: str, loan_amount: float,
                loan_source_id: int, created_by: str, melting: float = 0.0) -> list[dict]:
    conn = _get_connection(business_id)
    try:
        return _call_sp(conn, "iJewellery_Insert_Loan", [
            loan_number, loan_date, name, address, phone, metal_type,
            metal_price, item_type_id, item_weight, item_description,
            loan_amount, loan_source_id, created_by, melting,
        ])
    finally:
        conn.close()


def update_loan(business_id: int, loan_number: str, loan_date: datetime, name: str, address: str,
                phone: str, metal_type: str, metal_price: float, item_type_id: int,
                item_weight: float, item_description: str, loan_amount: float,
                loan_source_id: int, is_closure: int, created_by: str) -> list[dict]:
    conn = _get_connection(business_id)
    try:
        return _call_sp(conn, "iJewellery_Update_Loan", [
            loan_number, loan_date, name, address, phone, metal_type,
            metal_price, item_type_id, item_weight, item_description,
            loan_amount, loan_source_id, is_closure, created_by,
        ])
    finally:
        conn.close()


def update_loan_header(business_id: int, loan_number: str, loan_date: datetime,
                       loan_amount: float, updated_by: str) -> None:
    conn = _get_connection(business_id)
    try:
        _call_sp(conn, "iJewellery_Update_Loan_Header", [
            loan_number, loan_date, loan_amount, updated_by,
        ])
    finally:
        conn.close()


def insert_loan_multi(conn: pyodbc.Connection, loan_number: str, loan_date: datetime,
                      name: str, address: str, phone: str, loan_amount: float,
                      loan_source_id: int, created_by: str, customer_id: int) -> None:
    cursor = conn.cursor()
    cursor.execute(
        f"EXEC iJewellery_Insert_Loan_Multi ?,?,?,?,?,?,?,?,?",
        loan_number, loan_date, name, address, phone,
        loan_amount, loan_source_id, created_by, customer_id,
    )


def insert_loan_item_multi(conn: pyodbc.Connection, loan_number: str, metal_type: str,
                           metal_price: float, item_type_id: int, item_weight: float,
                           item_description: str, melting: float, created_by: str) -> None:
    cursor = conn.cursor()
    cursor.execute(
        f"EXEC iJewellery_Insert_Loan_Item_Multi ?,?,?,?,?,?,?,?",
        loan_number, metal_type, metal_price, item_type_id,
        item_weight, item_description, created_by, melting,
    )


def delete_loan_items(conn: pyodbc.Connection, loan_number: str) -> None:
    cursor = conn.cursor()
    cursor.execute("EXEC iJewellery_Delete_Loan_Items ?", loan_number)


def delete_loan(business_id: int, loan_number: str, created_by: str) -> list[dict]:
    conn = _get_connection(business_id)
    try:
        return _call_sp(conn, "iJewellery_Delete_Loan", [loan_number, created_by])
    finally:
        conn.close()


def update_loan_closure(business_id: int, loan_number: str, closure_date: datetime,
                        closure_amount: float, closure_comments: str, closure_by: str) -> list[dict]:
    conn = _get_connection(business_id)
    try:
        return _call_sp(conn, "iJewellery_UPDATE_Loan_Closure", [
            loan_number, closure_date, closure_amount, closure_comments, closure_by,
        ])
    finally:
        conn.close()


def update_loan_source(business_id: int, loan_number: str, loan_source_update_date: datetime,
                       new_loan_source_id: int, new_loan_source_amount: float,
                       description: str, created_by: str) -> list[dict]:
    conn = _get_connection(business_id)
    try:
        return _call_sp(conn, "iJewellery_Update_LoanSourceUpdateLog", [
            loan_number, loan_source_update_date, new_loan_source_id,
            new_loan_source_amount, description, created_by,
        ])
    finally:
        conn.close()


def update_part_loan(business_id: int, loan_number: str, new_loan_date: datetime,
                     net_payable_amount: float, additional_loan_amount: float,
                     created_by: str) -> list[dict]:
    conn = _get_connection(business_id)
    try:
        return _call_sp(conn, "iJewellery_Update_PartLoan", [
            loan_number, new_loan_date, net_payable_amount, additional_loan_amount, created_by,
        ])
    finally:
        conn.close()


# ---------- Master ----------

def get_all_villages(business_id: int) -> list[dict]:
    conn = _get_connection(business_id)
    try:
        return _call_sp(conn, "iJewellery_GET_ALL_Villages")
    finally:
        conn.close()


def get_all_item_types(business_id: int) -> list[dict]:
    conn = _get_connection(business_id)
    try:
        return _call_sp(conn, "iJewellery_GET_ALL_ItemType")
    finally:
        conn.close()


def get_all_metal_types(business_id: int) -> list[dict]:
    conn = _get_connection(business_id)
    try:
        return _call_sp(conn, "iJewellery_GET_ALL_MetalType")
    finally:
        conn.close()


def get_all_loan_sources(business_id: int) -> list[dict]:
    conn = _get_connection(business_id)
    try:
        return _call_sp(conn, "iJewellery_Get_All_LoanSource")
    finally:
        conn.close()


def get_all_loan_source_update_logs(business_id: int) -> list[dict]:
    conn = _get_connection(business_id)
    try:
        return _call_sp(conn, "iJewellery_Get_All_LoanSourceUpdateLog")
    finally:
        conn.close()


# ---------- Customer ----------

def upsert_customer(business_id: int, cust_id: int, customer_name: str, care_of_name: str,
                    phone: int, address_line1: str, address_line2: str, village: str,
                    created_by: str, is_update: bool) -> list[dict]:
    conn = _get_connection(business_id)
    try:
        return _call_sp(conn, "iJewellery_Upsert_Customer", [
            cust_id, customer_name, care_of_name, phone,
            address_line1, address_line2, village, created_by, is_update,
        ])
    finally:
        conn.close()


def get_customers_by_mobile(business_id: int, phone: str) -> list[dict]:
    conn = _get_connection(business_id)
    try:
        return _call_sp(conn, "ijewellery_GET_ALL_Customers_byMobile", [phone])
    finally:
        conn.close()


def get_customers_by_id(business_id: int, cust_id: int) -> list[dict]:
    conn = _get_connection(business_id)
    try:
        return _call_sp(conn, "ijewellery_GET_ALL_Customers_byCustID", [cust_id])
    finally:
        conn.close()


def get_customers_by_name(business_id: int, name: str) -> list[dict]:
    conn = _get_connection(business_id)
    try:
        return _call_sp(conn, "ijewellery_GET_ALL_Customers_byName", [name])
    finally:
        conn.close()


def get_customers_by_address(business_id: int, address: str) -> list[dict]:
    conn = _get_connection(business_id)
    try:
        return _call_sp(conn, "ijewellery_GET_ALL_Customers_byAddress", [address])
    finally:
        conn.close()


def insert_customer_ledger(business_id: int, customer_id: int, ledger_date: datetime,
                           credit: float, debit: float, invoice_no: str,
                           description: str, created_by: str) -> list[dict]:
    conn = _get_connection(business_id)
    try:
        return _call_sp(conn, "iJewellery_Insert_CustomerLedger", [
            customer_id, ledger_date, credit, debit, invoice_no, description, created_by,
        ])
    finally:
        conn.close()


def get_customer_ledger(business_id: int, customer_id: int) -> list[dict]:
    conn = _get_connection(business_id)
    try:
        return _call_sp(conn, "ijewellery_GET_ALL_CustomerLedger", [customer_id])
    finally:
        conn.close()


# ---------- Manage Customer (extended) ----------

def get_customers(business_id: int) -> list[dict]:
    conn = _get_connection(business_id)
    try:
        return _call_sp(conn, "usp_GetCustomers")
    finally:
        conn.close()


def get_customer_by_id(business_id: int, customer_id: int) -> list[dict]:
    conn = _get_connection(business_id)
    try:
        return _call_sp(conn, "usp_GetCustomerById", [customer_id])
    finally:
        conn.close()


def insert_customer(business_id: int, name: str, address: str, created_by: str) -> int:
    conn = _get_connection(business_id)
    try:
        cursor = conn.cursor()
        cursor.execute(
            "DECLARE @NewCustomerID BIGINT;"
            " EXEC usp_InsertCustomer @Name=?, @Address=?, @CreatedBy=?, @NewCustomerID=@NewCustomerID OUTPUT;"
            " SELECT @NewCustomerID",
            name, address, created_by,
        )
        row = cursor.fetchone()
        return int(row[0]) if row and row[0] is not None else 0
    finally:
        conn.close()


def update_customer(business_id: int, customer_id: int, name: str, address: str) -> None:
    conn = _get_connection(business_id)
    try:
        _call_sp(conn, "usp_UpdateCustomer", [customer_id, name, address])
    finally:
        conn.close()


def delete_customer(business_id: int, customer_id: int) -> None:
    conn = _get_connection(business_id)
    try:
        _call_sp(conn, "usp_DeleteCustomer", [customer_id])
    finally:
        conn.close()


def get_phones_by_customer(business_id: int, customer_id: int) -> list[dict]:
    conn = _get_connection(business_id)
    try:
        return _call_sp(conn, "usp_GetPhonesByCustomer", [customer_id])
    finally:
        conn.close()


def insert_customer_phone(business_id: int, customer_id: int, phone: str,
                          is_primary: bool, created_by: str) -> int:
    conn = _get_connection(business_id)
    try:
        cursor = conn.cursor()
        cursor.execute(
            "DECLARE @NewPhoneID BIGINT;"
            " EXEC usp_InsertCustomerPhone @CustomerID=?, @PhoneNumber=?, @IsPrimary=?, @CreatedBy=?, @NewPhoneID=@NewPhoneID OUTPUT;"
            " SELECT @NewPhoneID",
            customer_id, phone, is_primary, created_by,
        )
        row = cursor.fetchone()
        return int(row[0]) if row and row[0] is not None else 0
    finally:
        conn.close()


def delete_customer_phone(business_id: int, phone_id: int) -> None:
    conn = _get_connection(business_id)
    try:
        _call_sp(conn, "usp_DeleteCustomerPhone", [phone_id])
    finally:
        conn.close()


def set_primary_phone(business_id: int, customer_id: int, phone_id: int) -> None:
    conn = _get_connection(business_id)
    try:
        _call_sp(conn, "usp_SetPrimaryPhone", [customer_id, phone_id])
    finally:
        conn.close()


def merge_customers(business_id: int, master_id: int, duplicate_ids: str) -> list[dict]:
    conn = _get_connection(business_id)
    try:
        return _call_sp(conn, "usp_MergeCustomers", [master_id, duplicate_ids])
    finally:
        conn.close()


# ---------- Khatabook ----------

def khata_add_bill(business_id: int, customer_id: int, bill_no: str, bill_date: datetime,
                   amount: float, notes: str, created_by: str) -> int:
    conn = _get_connection(business_id)
    try:
        rows = _call_sp(conn, "usp_Khata_AddBill", [
            customer_id, bill_no, bill_date, amount, notes, created_by,
        ])
        return int(rows[0]["BillID"]) if rows else 0
    finally:
        conn.close()


def khata_add_debit_to_bill(business_id: int, bill_id: int, txn_date: datetime,
                             amount: float, notes: str, created_by: str) -> None:
    conn = _get_connection(business_id)
    try:
        _call_sp(conn, "usp_Khata_AddDebitToBill", [bill_id, txn_date, amount, notes, created_by])
    finally:
        conn.close()


def khata_add_payment(business_id: int, bill_id: int, txn_date: datetime,
                      amount: float, notes: str, created_by: str) -> None:
    conn = _get_connection(business_id)
    try:
        _call_sp(conn, "usp_Khata_AddPayment", [bill_id, txn_date, amount, notes, created_by])
    finally:
        conn.close()


def khata_get_customer_balances(business_id: int, show_all: bool = False) -> list[dict]:
    conn = _get_connection(business_id)
    try:
        return _call_sp(conn, "usp_Khata_GetCustomerBalances", [show_all])
    finally:
        conn.close()


def khata_get_customer_bills(business_id: int, customer_id: int) -> list[dict]:
    conn = _get_connection(business_id)
    try:
        return _call_sp(conn, "usp_Khata_GetCustomerBills", [customer_id])
    finally:
        conn.close()


def khata_get_all_bill_transactions(business_id: int, customer_id: int) -> list[dict]:
    conn = _get_connection(business_id)
    try:
        return _call_sp(conn, "usp_Khata_GetAllBillTransactions", [customer_id])
    finally:
        conn.close()


def khata_get_open_bills_for_payment(business_id: int, customer_id: int) -> list[dict]:
    conn = _get_connection(business_id)
    try:
        return _call_sp(conn, "usp_Khata_GetOpenBillsForPayment", [customer_id])
    finally:
        conn.close()


def khata_delete_transaction(business_id: int, txn_id: int, deleted_by: str) -> None:
    conn = _get_connection(business_id)
    try:
        _call_sp(conn, "usp_Khata_DeleteTransaction", [txn_id, deleted_by])
    finally:
        conn.close()


def khata_delete_bill(business_id: int, bill_id: int, deleted_by: str) -> None:
    conn = _get_connection(business_id)
    try:
        _call_sp(conn, "usp_Khata_DeleteBill", [bill_id, deleted_by])
    finally:
        conn.close()


# ---------- Entity / Customer Photos ----------

def update_entity_photo(business_id: int, entity_type: str, entity_id: int,
                        photo: bytes, content_type: str, updated_by: str) -> None:
    conn = _get_connection(business_id)
    try:
        cursor = conn.cursor()
        cursor.execute(
            "MERGE mchoksi.m_EntityPhoto AS t"
            " USING (SELECT ? AS EntityType, ? AS EntityID) AS s"
            "    ON t.EntityType = s.EntityType AND t.EntityID = s.EntityID"
            " WHEN MATCHED THEN"
            "     UPDATE SET Photo=?, PhotoContentType=?, UpdatedAt=GETDATE(), UpdatedBy=?"
            " WHEN NOT MATCHED THEN"
            "     INSERT (EntityType, EntityID, Photo, PhotoContentType, UpdatedAt, UpdatedBy)"
            "     VALUES (?, ?, ?, ?, GETDATE(), ?);",
            entity_type, entity_id,
            photo, content_type, updated_by,
            entity_type, entity_id, photo, content_type, updated_by,
        )
        conn.commit()
    finally:
        conn.close()


def get_entity_photo(business_id: int, entity_type: str, entity_id: int) -> tuple[bytes, str]:
    conn = _get_connection(business_id)
    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT Photo, PhotoContentType FROM mchoksi.m_EntityPhoto"
            " WHERE EntityType=? AND EntityID=?",
            entity_type, entity_id,
        )
        row = cursor.fetchone()
        if row and row[0] is not None:
            return (bytes(row[0]), str(row[1]))
        return (None, None)
    finally:
        conn.close()


def update_customer_photo(business_id: int, customer_id: int, photo: bytes,
                          content_type: str, updated_by: str) -> None:
    update_entity_photo(business_id, "Customer", customer_id, photo, content_type, updated_by)


def get_customer_photo(business_id: int, customer_id: int) -> tuple[bytes, str]:
    return get_entity_photo(business_id, "Customer", customer_id)


# ---------- Reports ----------

def get_interest_earned(business_id: int) -> list[dict]:
    conn = _get_connection(business_id)
    try:
        return _call_sp(conn, "iJewellery_Get_AllSourceWise_InterestEarned")
    finally:
        conn.close()


def get_daily_transaction(business_id: int) -> list[dict]:
    conn = _get_connection(business_id)
    try:
        return _call_sp(conn, "iJewellery_GET_DailyTransaction")
    finally:
        conn.close()


def get_loan_source_wise_total(business_id: int) -> list[dict]:
    conn = _get_connection(business_id)
    try:
        return _call_sp(conn, "RPT_GET_LoanSourceWiseAmountTotal")
    finally:
        conn.close()


def get_interest_dashboard_data(business_id: int) -> list[dict]:
    conn = _get_connection(business_id)
    try:
        return _call_sp(conn, "RPT_InterestEarnedFromClosure")
    finally:
        conn.close()


# ---------- Metal Rates ----------

def update_metal_rates(business_id: int, gold_rate: float, silver_rate: float, created_by: str) -> bool:
    conn = _get_connection(business_id)
    try:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO mchoksi.MetalRates (RateDate, GoldRate, SilverRate, CreatedAt, CreatedBy)"
            " VALUES (GETDATE(), ?, ?, GETDATE(), ?)",
            gold_rate, silver_rate, created_by,
        )
        conn.commit()
        return cursor.rowcount > 0
    finally:
        conn.close()


def get_latest_metal_rates(business_id: int) -> dict:
    try:
        conn = _get_connection(business_id)
        try:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT TOP 1 GoldRate, SilverRate FROM mchoksi.MetalRates ORDER BY CreatedAt DESC"
            )
            row = cursor.fetchone()
            if row:
                return {"gold": float(row[0]), "silver": float(row[1])}
        finally:
            conn.close()
    except Exception:
        pass
    return {"gold": 0.0, "silver": 0.0}


# ---------- Borrowed Loans ----------

def get_all_borrowed_loans(business_id: int, filter_status: str = "ALL") -> list[dict]:
    conn = _get_connection(business_id)
    try:
        return _call_sp(conn, "iJewellery_Get_All_BorrowedLoans", [filter_status])
    finally:
        conn.close()


def get_borrowed_loan_by_id(business_id: int, borrowed_loan_id: int) -> list[dict]:
    conn = _get_connection(business_id)
    try:
        return _call_sp(conn, "iJewellery_Get_BorrowedLoan_ByID", [borrowed_loan_id])
    finally:
        conn.close()


def insert_borrowed_loan(business_id: int, borrowing_date: datetime, party_name: str,
                         party_contact: str, party_address: str, principal_amount: float,
                         interest_rate: float, interest_type: str, due_date: datetime,
                         notes: str, created_by: str) -> int:
    conn = _get_connection(business_id)
    try:
        rows = _call_sp(conn, "iJewellery_Insert_BorrowedLoan", [
            borrowing_date, party_name, party_contact, party_address,
            principal_amount, interest_rate, interest_type, due_date,
            notes, created_by,
        ])
        return int(rows[0]["BorrowedLoanID"]) if rows else 0
    finally:
        conn.close()


def update_borrowed_loan(business_id: int, borrowed_loan_id: int, borrowing_date: datetime,
                         party_name: str, party_contact: str, party_address: str,
                         principal_amount: float, interest_rate: float, interest_type: str,
                         due_date: datetime, notes: str, updated_by: str) -> None:
    conn = _get_connection(business_id)
    try:
        _call_sp(conn, "iJewellery_Update_BorrowedLoan", [
            borrowed_loan_id, borrowing_date, party_name, party_contact, party_address,
            principal_amount, interest_rate, interest_type, due_date, notes, updated_by,
        ])
    finally:
        conn.close()


def close_borrowed_loan(business_id: int, borrowed_loan_id: int, closure_date: datetime,
                        closure_amount: float, closure_notes: str, closed_by: str) -> None:
    conn = _get_connection(business_id)
    try:
        _call_sp(conn, "iJewellery_Close_BorrowedLoan", [
            borrowed_loan_id, closure_date, closure_amount, closure_notes, closed_by,
        ])
    finally:
        conn.close()


def delete_borrowed_loan(business_id: int, borrowed_loan_id: int, deleted_by: str) -> None:
    conn = _get_connection(business_id)
    try:
        _call_sp(conn, "iJewellery_Delete_BorrowedLoan", [borrowed_loan_id, deleted_by])
    finally:
        conn.close()


# ---------- API Logging ----------

async def log_api_call(business_id: int, method: str, url: str, request_body: str,
                       response_body: str, status_code: int, execution_time_ms: int,
                       user_agent: str, client_ip: str, exception: str) -> None:
    try:
        conn = _get_connection(business_id)
        cursor = conn.cursor()
        cursor.execute(
            "{CALL usp_LogApiCall(?,?,?,?,?,?,?,?,?)}",
            method, url, request_body or "", response_body or "",
            status_code, execution_time_ms, user_agent or "",
            client_ip or "", exception,
        )
        conn.commit()
        conn.close()
    except Exception:
        pass
