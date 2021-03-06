from datetime import datetime, timedelta

from pydantic import BaseModel
from typing import Optional

from fastapi import FastAPI, status, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from jose import JWTError, jwt
from passlib.context import CryptContext

from core.data.models.auth.token import Token
from core.data.models.user.model import User

from core.data.services.user import user as UserService

from core.security.auth import oauth

SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

async def verify_password(password: str, password_hash: str):
    return pwd_context.verify(password, password_hash)

async def get_password_hash(password: str):
    return pwd_context.hash(password)

async def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expires_in = datetime.utcnow() + expires_delta
    else:
        # Set timedelta for one week
        expires_in = datetime.utcnow() + timedelta(minutes=10080)
    # Generate Refresh Token
    # Generate Scope
    to_encode.update({"exp": expires_in})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    # Token expires_in field is int
    expires_in_ms = expires_in.microsecond * 1000
    return {
            "access_token": encoded_jwt,
            "refresh_token": "",
            "token_type": "bearer",
            "scope": "",
            "expires_in": expires_in_ms
        }

async def get_current_user(access_token: str):
    data = jwt.decode(access_token, SECRET_KEY, algorithms=[ALGORITHM])
    user_id = data.get("_id", None)
    if user_id is None:
        return None
    user: User = await UserService.get_user(user_id)
    return user

    

async def authenticate_user(password: str, password_hash: str):
    if not await verify_password(password, password_hash):
        return False
    return True

async def validate_user_access(token, cfg):
    credentials_cfg = {
        "user_crud": ["admin", "user"]
    }
    user_credentials = await oauth.get_token_credentials(token)
    if user_credentials:
        valid_credentials = credentials_cfg[cfg]
        for cred in user_credentials:
            if cred in valid_credentials:
                return True
    return False
