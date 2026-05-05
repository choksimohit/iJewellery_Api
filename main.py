from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routers import admin, auth, borrowed_loans, customer, khatabook, loan, master, reports

app = FastAPI(
    title="iJewellery API",
    version="1.0.0",
    description="Jewellery loan management API — FastAPI port of iJewelleryApi (.NET 9)",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(loan.router)
app.include_router(customer.router)
app.include_router(master.router)
app.include_router(reports.router)
app.include_router(borrowed_loans.router)
app.include_router(khatabook.router)
app.include_router(admin.router)


@app.get("/", tags=["Health"])
def root():
    return {"status": "ok", "app": "iJewellery FastAPI"}
