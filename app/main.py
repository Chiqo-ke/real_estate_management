from fastapi import FastAPI
from .routers import (
    properties_router,
    tenants_router,
    leases_router,
    invoices_router,
    payments_router,
    auth_router,
    debts_router
)
from .config import settings

app = FastAPI(title="Real Estate Management System")

# Include routers
routers = [
    properties_router,
    tenants_router,
    leases_router,
    invoices_router,
    payments_router,
    auth_router,
    debts_router
]

for router in routers:
    app.include_router(router, prefix=settings.API_V1_STR)

@app.get("/")
def read_root():
    return {"message": "Welcome to Real Estate Management System"}
