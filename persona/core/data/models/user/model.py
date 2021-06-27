from typing import Optional
from pydantic import BaseModel, EmailStr, Field

class User(BaseModel):
    firstname: str = Field(...)
    lastname: str = Field(...)
    username: str = Field(...)
    email: EmailStr = Field(...)
    password_hash: str = Field(...)
    age: int = Field(..., gt=13)
    is_active: bool = Field(...)
    credentials: list = Field(...)
    keychain: dict = Field(...)
