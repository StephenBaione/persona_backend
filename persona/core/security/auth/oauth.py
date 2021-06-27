from datetime import datetime, timedelta

from typing import Optional

from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from jose import JWTError, jwt
from passlib.context import CryptContext

from core.data.db import db
from core.data.models.auth.token import Token
from core.data.models.user.model import User

SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# TODO:// Create token validation function and make sure that it checks for expiration as well
async def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    # Encode username for now
    to_encode = {"_id", data["_id"]}
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        # Set timedelta for one week
        expire = datetime.utcnow() + timedelta(minutes=10080)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return {"access_token": encoded_jwt, "token_type": "bearer"}

async def get_token_credentials(token):
    try:
        decoded_token = jwt.decode(token, SECRET_KEY, algorithms=ALGORITHM)
        user_id = decoded_token["_id"]
        user_credentials = await db.get_user_field(user_id, "credentials")
        return user_credentials
    except Exception as e:
        return None
