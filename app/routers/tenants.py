from fastapi import APIRouter

router = APIRouter(prefix="/tenants", tags=["tenants"])

@router.get("/")
async def get_tenants():
    return {"message": "List of tenants"}
