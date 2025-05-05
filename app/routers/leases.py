from fastapi import APIRouter

router = APIRouter(prefix="/leases", tags=["leases"])

@router.get("/")
async def get_leases():
    return {"message": "List of leases"}
