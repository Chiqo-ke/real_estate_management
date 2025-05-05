from fastapi import APIRouter

router = APIRouter(prefix="/invoices", tags=["invoices"])

@router.get("/")
async def get_invoices():
    return {"message": "List of invoices"}
