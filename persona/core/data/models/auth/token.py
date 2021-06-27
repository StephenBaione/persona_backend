from typing import Optional

from pydantic import BaseModel

class Token(BaseModel):
    access_token: str
    refresh_token: Optional[str] = None
    token_type: str
    scope: Optional[str] = None
    expires_in: Optional[int] = None

class TokenData(BaseModel):
    username: Optional[str] = None
