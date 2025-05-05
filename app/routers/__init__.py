from .properties import router as properties_router
from .tenants import router as tenants_router
from .leases import router as leases_router
from .invoices import router as invoices_router
from .payments import router as payments_router
from .auth import router as auth_router
from .debts import router as debts_router

__all__ = [
    'properties_router',
    'tenants_router',
    'leases_router',
    'invoices_router',
    'payments_router',
    'auth_router',
    'debts_router'
]
