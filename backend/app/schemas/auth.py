from pydantic import BaseModel, EmailStr
from typing import Optional

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserRegister(BaseModel):
    email: EmailStr
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class TokenRefresh(BaseModel):
    refresh_token: str

class UserProfile(BaseModel):
    id: int
    email: EmailStr
    username: str
    hyperliquid_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None

    class Config:
        from_attributes = True