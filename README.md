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
├── .env.example          # Template — copy to .env and fill in values
├── requirements.txt
├── models/
│   ├── loan.py           # Loan request/response Pydantic models
│   ├── customer.py       # Customer Pydantic models
│   └── auth.py           # Login request model
└── routers/
    ├── auth.py           # POST /login, GET /getUserAuthenticationAll
    ├── loan.py           # 15 loan endpoints (JWT protected)
    ├── customer.py       # 7 customer endpoints
    ├── master.py         # 5 master data endpoints
    └── reports.py        # 4 report endpoints
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
| POST | `/insertLoan` | Create a new loan |
| POST | `/updateLoan` | Update an existing loan |
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
| GET | `/getLoanTransactions` | Get transaction history |
| GET | `/getMissingLoanNumbers` | Find gaps in loan numbering |
| GET | `/getLoanByLoanAmountGreaterThan` | Filter by amount threshold |
| GET | `/getLoanByNameSearchQuery` | Name-based full-text search |
| GET | `/getNextLoanNumber` | Get next available loan number |
| GET | `/getMonthsBetween` | Calculate months between two dates |

### Customer — `/api/customer`

| Method | Endpoint | Description |
|---|---|---|
| POST | `/upsertCustomer` | Create or update a customer |
| GET | `/getCustomersByMobile` | Find customer by phone |
| GET | `/getCustomersById` | Find customer by ID |
| GET | `/getCustomersByName` | Search customers by name |
| GET | `/getCustomersByAddress` | Search customers by address |
| POST | `/insertCustomerLedger` | Add a ledger entry (credit/debit) |
| GET | `/getCustomerLedger` | Get customer ledger history |

### Master Data — `/api/masterData`

| Method | Endpoint | Description |
|---|---|---|
| GET | `/getAllVillages` | List all villages |
| GET | `/getAllItemTypes` | List jewellery item types |
| GET | `/getAllMetalTypes` | List metal types |
| GET | `/getAllLoanSources` | List loan sources/funders |
| GET | `/getAllLoanSourceUpdateLogs` | History of source changes |

### Reports — `/api/reports`

| Method | Endpoint | Description |
|---|---|---|
| GET | `/getInterestEarned` | Interest earned report |
| GET | `/getDailyTransaction` | Daily transaction summary |
| GET | `/getLoanTransactions` | Loan transaction history |
| GET | `/getLoanSourceWiseAmountTotal` | Amount totals by loan source |

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
