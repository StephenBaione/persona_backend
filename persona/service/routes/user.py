from fastapi import APIRouter, Body
from fastapi.encoders import jsonable_encoder

from core.data.db import db
from core.data.models.user.model import User

router = APIRouter(prefix="/user", tags=["user"])

# TODO:// Write null checks for these methods
@router.post("/", response_description="user retrieved")
async def get_user_data(user_id: str) -> dict:
    user_id = jsonable_encoder(user_id)
    success, user_data = await db.get_user(user_id)
    user_data['_id'] = str(user_data['_id'])
    return {
        "success": success,
        "user_data": user_data
    }


@router.post("/add", response_description="user added")
async def add_user_data(user: User = Body(...)) -> dict:
    user = jsonable_encoder(user)
    success, user_data = await db.add_user(user)
    user_data['_id'] = str(user_data["_id"])
    print(success, user_data)
    return {
        "success": success,
        "user": user_data
    }

@router.post("/update", response_description="user updated")
async def update_user_data(user: User = Body(...)) -> dict:
    user = jsonable_encoder(user)
    success, user_data = await db.update_user(user)
    user_data['_id'] = str(user_data["_id"])
    print(success, user_data)
    return {
        "success": success,
        "user": user_data
    }
