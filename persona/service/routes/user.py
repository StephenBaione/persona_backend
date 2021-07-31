from typing import Any, Optional

from fastapi import APIRouter, Body, HTTPException, status, Header, Response, Request
from fastapi.encoders import jsonable_encoder
from fastapi.param_functions import Cookie
from fastapi.templating import Jinja2Templates

from core.data.db import db
from core.data.models.user.model import User
from core.data.models.auth.token import Token
from core.data.services.user import user as UserService

from core.security.auth import user_auth

from service.internal.user import handle_user_auth

router = APIRouter(prefix="/user", tags=["user"])

templates = Jinja2Templates(directory="templates")

# TODO:// Write helper function for processing db returns
@router.get("/all", response_description="all users retrieved")
async def get_all_user_data(token: str = Header(None)) -> dict:
    if not await user_auth.validate_user_access(token, "user_crud"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    users = await db.get_all_users()
    for user in users:
        user["_id"] = str(user["_id"])
    return {
        "success": True,
        "users": users
    }

# TODO:// Write null checks for these methods
@router.get("/get", response_description="user retrieved")
async def get_user_data(user_id: str, token: str = Header(None), _id: Optional[str] = Cookie(None)) -> dict:
    print("\n\n-------- Supplied Token --------\n\n", token)
    if not await user_auth.validate_user_access(token, "user_crud"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user_id = jsonable_encoder(user_id)
    if _id:
        print("Id is not none")
        if _id == user_id:
            print("Cookie is valid")
    user_data = await db.get_user(user_id)
    user_data['_id'] = str(user_data['_id'])
    return {
        "success": True,
        "user_data": user_data
    }


@router.post("/add", response_description="user added")
async def add_user_data(user: User = Body(...), token: str = Header(None)) -> dict:
    if not await user_auth.validate_user_access(token, "user_crud"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user = jsonable_encoder(user)
    # TODO:// Remove hashing password. This should be done in signup endpoint
    user["password_hash"] = await user_auth.get_password_hash(user["password_hash"])
    user_data = await db.add_user(user)
    user_data['_id'] = str(user_data["_id"])
    return {
        "success": True,
        "user": user_data
    }

@router.post("/update", response_description="user updated")
async def update_user_data(user: User = Body(...), token: str = Header(None)) -> dict:
    if not await user_auth.validate_user_access(token, "user_crud"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user = jsonable_encoder(user)
    user_data = await db.update_user(user)
    user_data['_id'] = str(user_data["_id"])
    return {
        "success": True,
        "user": user_data
    }

@router.post("/delete", response_description="user deleted")
async def delete_user(user_id: str, token: str = Header(None)) -> dict:
    if not await user_auth.validate_user_access(token, "user_crud"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user_id = jsonable_encoder(user_id)
    user_data = await db.delete_user(user_id)
    user_data["_id"] = str(user_data["_id"])
    return {
        "success": True,
        "user": user_data
    }

@router.post("/delete_all", response_description="all users deleted")
async def delete_all_users(token: str = Header(None)) -> dict:
    if not await user_auth.validate_user_access(token, "user_crud"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    success = await db.delete_all_users()
    return {
        "success": success
    }

# TODO:// Make password in post requests secure
# TODO:// Move authentication to separate router
# TODO:// Store Token in database
@router.post("/auth/login", response_model=Any, response_description="login user")
async def login_user(request: Request, response: Response, username: str = Body(...), password: str = Body(...)):
    print("\n\n-------- Login --------\n\n", username, password)
    user = await db.get_user_by_field("username", username)
    password_hash = user["password_hash"]
    result = await user_auth.authenticate_user(password, password_hash)
    if result:
        user["_id"] = str(user["_id"])
        token = await user_auth.create_access_token(user)
        response.set_cookie("_id", user["_id"], samesite="Lax", secure=False)
        return {
            "token": token,
            "_id": user["_id"]
        }
    raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

@router.post("/auth/signup", response_model=Token, response_description="login user")
async def signup_user(response: Response, user_data: User = Body(...)):
    user_data = jsonable_encoder(user_data)
    user_data.credentials.append("user")
    password = user_data['password_hash']
    password_hash = await user_auth.get_password_hash(password)
    user_data["password_hash"] = password_hash
    user = await UserService.add_user(user_data)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unable to signup user",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user["_id"] = str(user["_id"])
    token = await user_auth.create_access_token(user)

    return token
