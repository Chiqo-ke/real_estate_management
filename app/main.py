from fastapi import FastAPI
from .routers import (
    properties_router,
    tenants_router,
    leases_router,
    invoices_router,
    payments_router
)
from .routers.auth import router as auth_router
from .config import settings

app = FastAPI(title="Real Estate Management System")

# Include routers
app.include_router(properties_router, prefix=settings.API_V1_STR)
app.include_router(tenants_router, prefix=settings.API_V1_STR)
app.include_router(leases_router, prefix=settings.API_V1_STR)
app.include_router(invoices_router, prefix=settings.API_V1_STR)
app.include_router(payments_router, prefix=settings.API_V1_STR)
app.include_router(auth_router, prefix=settings.API_V1_STR)

@app.get("/")
def read_root():
    return {"message": "Welcome to Real Estate Management System"}
