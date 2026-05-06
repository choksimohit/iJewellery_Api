# iJewellery FastAPI

A Python/FastAPI port of the original **iJewelleryApi** (.NET 9 / ASP.NET Core) project.  
The SQL Server database and all stored procedures remain **unchanged** — only the application layer is rewritten in Python.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Framework | FastAPI 0.115 |
| Server | Uvicorn |
| Database Driver | pyodbc (SQL Server) |
| Authentication | JWT via python-jose |
| Validation | Pydantic v2 |
| Config | pydantic-settings + .env |

---

## Project Structure

```
iJewellery_FastAPI/
├── main.py               # App entry point, CORS, router registration
├── config.py             # Settings loaded from .env file
├── database.py           # All SQL Server / stored procedure calls
├── auth.py               # JWT create/decode, FastAPI dependencies
├── generate_excel.py     # Excel report generation utilities
├── .env.example          # Template — copy to .env and fill in values
├── requirements.txt
├── models/
│   ├── loan.py           # Loan request/response Pydantic models
│   ├── customer.py       # Customer Pydantic models
│   ├── borrowed_loan.py  # Borrowed loan Pydantic models
│   ├── khatabook.py      # Khatabook Pydantic models
│   ├── admin.py          # Admin Pydantic models
│   └── auth.py           # Login request model
└── routers/
    ├── auth.py           # POST /login, GET /getUserAuthenticationAll
    ├── loan.py           # 20 loan endpoints (JWT protected)
    ├── customer.py       # 18 customer endpoints (JWT protected)
    ├── master.py         # 5 master data endpoints (JWT protected)
    ├── reports.py        # 5 report endpoints (JWT protected)
    ├── borrowed_loans.py # 6 borrowed loan endpoints
    ├── khatabook.py      # 9 khatabook endpoints
    └── admin.py          # 9 admin endpoints
```

---

## Setup

### 1. Prerequisites

- Python 3.11+
- [ODBC Driver 17 for SQL Server](https://learn.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server) installed on your machine

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure environment

```bash
cp .env.example .env
```

Edit `.env` with your actual values:

```env
SERVER_NAME=your_sql_server_host
DB_USERNAME=your_db_user
DB_PASSWORD=your_db_password
JWT_KEY=your_jwt_secret_key
JWT_ISSUER=iJewellery
JWT_AUDIENCE=iJewellery
BUSINESS_DB_1=iJewellery
BUSINESS_DB_2=iJewellery_radhe
```

> `JWT_KEY` must match the key used in the original .NET app so existing tokens remain valid.

### 4. Run the server

```bash
uvicorn main:app --reload --port 8000
```

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

---

## API Endpoints

### Auth — `/api/auth`

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| POST | `/login` | No | Login and get JWT token |
| GET | `/getUserAuthenticationAll` | No | Get page-level user permissions |

### Loan — `/api/loan` *(all require JWT)*

| Method | Endpoint | Description |
|---|---|---|
| POST | `/insertLoan` | Create a new single-item loan |
| POST | `/insertLoanMulti` | Create a loan with multiple items (transactional) |
| POST | `/updateLoan` | Update an existing loan |
| POST | `/updateLoanHeader` | Update loan date and amount only |
| DELETE | `/deleteLoan` | Delete a loan |
| GET | `/getAllLoans` | Get loan by loan number |
| GET | `/getAllLoansByMobile` | Search loans by phone |
| GET | `/getAllLoansByName` | Search loans by customer name |
| GET | `/getAllLoansByAddress` | Search loans by address |
| GET | `/getAllLoansBySource` | Filter loans by source |
| GET | `/getLoanForClosure` | Get loan details for closure |
| POST | `/updateLoanClosure` | Close a loan |
| POST | `/updateLoanSource` | Change loan funder/source |
| POST | `/updatePartLoan` | Process a partial loan update |
| GET | `/getLoanTransactions` | Get transaction history for a loan |
| GET | `/getMissingLoanNumbers` | Find gaps in loan numbering |
| GET | `/getLoanByLoanAmountGreaterThan` | Filter by amount threshold and source |
| GET | `/getLoanByNameSearchQuery` | Name-based full-text search |
| GET | `/getNextLoanNumber` | Get next available loan number |
| GET | `/getMonthsBetween` | Calculate months between two dates |

### Customer — `/api/customer` *(all require JWT)*

| Method | Endpoint | Description |
|---|---|---|
| POST | `/upsertCustomer` | Create or update a customer (legacy) |
| GET | `/getCustomersByMobile` | Find customer by phone (legacy) |
| GET | `/getCustomersById` | Find customer by ID (legacy) |
| GET | `/getCustomersByName` | Search customers by name (legacy) |
| GET | `/getCustomersByAddress` | Search customers by address (legacy) |
| POST | `/insertCustomerLedger` | Add a ledger entry (credit/debit) |
| GET | `/getCustomerLedger` | Get customer ledger history |
| GET | `/getCustomers` | List all customers |
| GET | `/getCustomerById` | Get a single customer by ID |
| POST | `/insertCustomer` | Create a new customer |
| POST | `/updateCustomer` | Update a customer's name and address |
| DELETE | `/deleteCustomer` | Delete a customer |
| GET | `/getPhonesByCustomer` | List all phone numbers for a customer |
| POST | `/insertCustomerPhone` | Add a phone number to a customer |
| DELETE | `/deleteCustomerPhone` | Remove a phone number |
| POST | `/setPrimaryPhone` | Set the primary phone for a customer |
| POST | `/mergeCustomers` | Merge duplicate customer records |
| POST | `/updateEntityPhoto` | Upload a photo for any entity type (multipart) |
| GET | `/getEntityPhoto` | Retrieve a photo for any entity type |
| POST | `/updateCustomerPhoto` | Upload a customer profile photo (multipart) |
| GET | `/getCustomerPhoto` | Retrieve a customer profile photo |

### Master Data — `/api/masterData` *(all require JWT)*

| Method | Endpoint | Description |
|---|---|---|
| GET | `/getAllVillages` | List all villages |
| GET | `/getAllItemTypes` | List jewellery item types |
| GET | `/getAllMetalTypes` | List metal types |
| GET | `/getAllLoanSources` | List loan sources/funders |
| GET | `/getAllLoanSourceUpdateLogs` | History of loan source changes |

### Reports — `/api/reports` *(all require JWT)*

| Method | Endpoint | Description |
|---|---|---|
| GET | `/getInterestEarned` | Interest earned report |
| GET | `/getDailyTransaction` | Daily transaction summary |
| GET | `/getLoanTransactions` | Loan transaction history |
| GET | `/getLoanSourceWiseAmountTotal` | Amount totals by loan source |
| GET | `/getInterestDashboardData` | Interest dashboard summary data |

### Borrowed Loans — `/api/borrowedLoans`

| Method | Endpoint | Description |
|---|---|---|
| GET | `/getAll` | List all borrowed loans (filter by status: ALL/OPEN/CLOSED) |
| GET | `/getById` | Get a single borrowed loan by ID |
| POST | `/insert` | Create a new borrowed loan |
| POST | `/update` | Update an existing borrowed loan |
| POST | `/close` | Close a borrowed loan with closure details |
| DELETE | `/delete` | Delete a borrowed loan |

### Khatabook — `/api/khatabook`

| Method | Endpoint | Description |
|---|---|---|
| POST | `/addBill` | Create a new bill for a customer |
| POST | `/addDebitToBill` | Add a debit transaction to a bill |
| POST | `/addPayment` | Record a payment against a bill |
| GET | `/getCustomerBalances` | Get outstanding balances for all customers |
| GET | `/getCustomerBills` | List all bills for a customer |
| GET | `/getAllBillTransactions` | Get all transactions for a customer's bills |
| GET | `/getOpenBillsForPayment` | Get open (unpaid) bills for a customer |
| DELETE | `/deleteTransaction` | Delete a bill transaction |
| DELETE | `/deleteBill` | Delete a bill |

### Admin — `/api/admin`

| Method | Endpoint | Description |
|---|---|---|
| GET | `/getUserAuthorizations` | List all user authorization records |
| POST | `/insertUserAuthorization` | Grant a user access to a page |
| POST | `/updateUserAuthorization` | Update a user's page authorization |
| DELETE | `/deleteUserAuthorization` | Revoke a user's page authorization |
| GET | `/getMenuPages` | List all registered menu pages |
| POST | `/insertMenuPage` | Register a new menu page |
| POST | `/updateMenuPage` | Update a menu page's properties |
| DELETE | `/deleteMenuPage` | Remove a menu page |
| POST | `/updateMetalRates` | Update current gold/silver rates |
| GET | `/getLatestMetalRates` | Get the latest gold/silver rates |

---

## Authentication

The API uses **JWT Bearer tokens**.

1. Call `POST /api/auth/login` with your username, password, and business_id
2. Copy the `access_token` from the response
3. Include it in all protected requests:
   ```
   Authorization: Bearer <your_token>
   ```

The token contains a `BusinessId` claim which automatically routes your requests to the correct database (multi-tenant).

---

## Multi-Tenant Design

Each business has its own database. The `BusinessId` in the JWT claim determines which database is used for every request:

| BusinessId | Database |
|---|---|
| 1 | iJewellery (default) |
| 2 | iJewellery_radhe |

Configure additional databases in `.env` as `BUSINESS_DB_3`, etc., and update `config.py`.

---

## Original Project

The original .NET 9 API lives at:
```
c:\Users\lenovo\source\repos\iJewelleryLoans\iJewelleryApi\
```
Both projects share the **same SQL Server database** and stored procedures.
