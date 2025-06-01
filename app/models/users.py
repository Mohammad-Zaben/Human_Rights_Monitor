from pydantic import BaseModel, Field, HttpUrl, EmailStr
from typing import Optional
from enum import Enum

class UserType(str, Enum):
    admin = "admin"
    user = "user"
    organization = "organization"
    lawyer = "lawyer"

class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    role: UserType
    phone: Optional[str] = Field(None, min_length=10, max_length=15)  
    preferred_contact_method: Optional[str] = Field(None, max_length=50)  
    id: Optional[str] = None
    organization_name: Optional[str] = Field(None, max_length=100)

class UserCreate(UserBase):
    password: str = Field(..., min_length=8, max_length=128)

    model_config = {
        "json_schema_extra": {
            "example": {
                "username": "johndoe",
                "email": "johndoe@example.com",
                "role": "user",
                "phone": "1234567890",
                "preferred_contact_method": "email",
                "organization_name": "Example Organization",
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

