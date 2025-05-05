from fastapi import APIRouter

router = APIRouter(
    prefix="/debts",
    tags=["debts"]
)

@router.get("/occupied")
async def get_occupied_debts():
    """
    Returns a list of currently occupied properties with their outstanding debts.
    Each item includes property details, tenant information, and the amount owed.
    """
    return {
        "occupied_debts": [
            {
                "property_id": "prop123",
                "property_name": "Sample Property",
                "tenant_name": "John Doe",
                "outstanding_amount": 1500.00,
                "last_payment_date": "2023-01-15"
            }
        ]
    }
