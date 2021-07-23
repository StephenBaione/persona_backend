from typing import Optional

from pydantic import BaseModel, Field, EmailStr

class User(BaseModel):
    user_id: str = Field(...)
    display_name: str = Field(...)
    email: str = EmailStr(...)
    explicit_content: dict = Field(
        default= {
            "explicit_content": {
                "filter_enabled": False,
                "filter_locked": False
            }
        })
    external_urls: dict = Optional[Field(default=None)]
    followers: dict = Field(...)
    href: str = Field(...)
    images: list = Field(...)
    product: str = Field(...)
    type: str = Field(...)
    uri: str = Field(...)

