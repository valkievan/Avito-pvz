from typing import Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


class UserBase(BaseModel):
    email: EmailStr
    role: str = Field(..., pattern="^(employee|moderator)$")


class UserCreate(UserBase):
    password: str


class UserInDB(UserBase):
    id: UUID
    password_hash: str


class User(UserBase):
    id: UUID


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    user_id: Optional[UUID] = None
    role: Optional[str] = None


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class DummyLoginRequest(BaseModel):
    role: str = Field(..., pattern="^(employee|moderator)$")
