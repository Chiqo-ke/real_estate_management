from fastapi import APIRouter

router = APIRouter(prefix="/payments", tags=["payments"])

@router.get("/")
async def get_payments():
    return {"message": "List of payments"}
