from fastapi import APIRouter, Body, HTTPException, status
from fastapi.encoders import jsonable_encoder

from core.data.db import db
from core.data.models.user.model import User
from core.data.models.auth.token import Token

from core.security.auth import user_auth

router = APIRouter(prefix="/user", tags=["user"])

# TODO:// Write helper function for processing db returns
@router.get("/all", response_description="all users retrieved")
async def get_all_user_data() -> dict:
    success, users = await db.get_all_users()
    for user in users:
        user["_id"] = str(user["_id"])
    return {
        "success": success,
        "users": users
    }

# TODO:// Write null checks for these methods
@router.get("/get", response_description="user retrieved")
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
    # TODO:// Remove hashing password. This should be done in signup endpoint
    user["password_hash"] = await user_auth.get_password_hash(user["password_hash"])
    success, user_data = await db.add_user(user)
    user_data['_id'] = str(user_data["_id"])
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

@router.post("/delete", response_description="user deleted")
async def delete_user(user_id: str) -> dict:
    user_id = jsonable_encoder(user_id)
    success, user_data = await db.delete_user(user_id)
    user_data["_id"] = str(user_data["_id"])
    return {
        "success": success,
        "user": user_data
    }

@router.post("/delete_all", response_description="all users deleted")
async def delete_all_users() -> dict:
    success = await db.delete_all_users()
    return {
        "success": success
    }

@router.post("/auth/login", response_model=Token, response_description="login user")
async def login_user(username: str = Body(...), password: str = Body(...)):
    success, user = await db.get_user_by_field("username", username)
    password_hash = user["password_hash"]
    result = await user_auth.authenticate_user(password, user)
    if result:
        user["_id"] = str(user["_id"])
        token = await user_auth.create_access_token(user)
        return token
    raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
