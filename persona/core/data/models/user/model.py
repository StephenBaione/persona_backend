from typing import Optional
from pydantic import BaseModel, EmailStr, Field

class User(BaseModel):
    firstname: str = Field(...)
    lastname: str = Field(...)
    username: str = Field(...)
    email: EmailStr = Field(...)
    age: int = Field(..., gt=13)

