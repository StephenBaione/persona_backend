from fastapi import APIRouter

router = APIRouter()

from service import internal

@router.get("/users/", tags=["users"])
async def read_users():
    return {"username": "test"}
