from datetime import datetime, timedelta

from pydantic import BaseModel
from typing import Optional

from fastapi import FastAPI, status, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from jose import JWTError, jwt
from passlib.context import CryptContext

from core.data.models.auth.token import Token
from core.data.models.user.model import User

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
        expire = datetime.utcnow() + expires_delta
    else:
        # Set timedelta for one week
        expire = datetime.utcnow() + timedelta(minutes=10080)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return {"access_token": encoded_jwt, "token_type": "bearer"}

async def authenticate_user(password: str, password_hash: str):
    if not await verify_password(password, password_hash):
        return False
    return True

async def validate_user_access(token, cfg):
    credentials_cfg = {
        "user_crud": ["admin"]
    }
    user_credentials = await oauth.get_token_credentials(token)
    if user_credentials:
        valid_credentials = credentials_cfg[cfg]
        for cred in user_credentials:
            if cred in valid_credentials:
                return True
    return False
