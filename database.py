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
                loan_source_id: int, created_by: str) -> list[dict]:
    conn = _get_connection(business_id)
    try:
        return _call_sp(conn, "iJewellery_Insert_Loan", [
            loan_number, loan_date, name, address, phone, metal_type,
            metal_price, item_type_id, item_weight, item_description,
            loan_amount, loan_source_id, created_by,
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
