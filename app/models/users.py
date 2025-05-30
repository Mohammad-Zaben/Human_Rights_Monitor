from pydantic import BaseModel, Field, HttpUrl, EmailStr
from typing import Optional
from enum import Enum

class UserType(str, Enum):
    admin = "admin"
    user = "user"
    organization = "organization"

class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    role: UserType
    id: Optional[str] = None

class UserCreate(UserBase):
    password: str = Field(..., min_length=8, max_length=128)

    model_config = {
        "json_schema_extra": {
            "example": {
                "username": "johndoe",
                "email": "johndoe@example.com",
                "role": "user",
                "password": "securepassword123"
            }
        }
    }

class UserInDB(UserBase):
    hashed_password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: str | None = None

