import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field


class UserRegister(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)
    full_name: Optional[str] = None


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    id: uuid.UUID
    email: EmailStr
    full_name: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    # the provided testing client's auto-fill logic looks for `body.token`
    # specifically, so this is just an alias of access_token for compatibility
    # with that client - access_token stays the "real"/standard field name
    token: str


class FileOut(BaseModel):
    id: uuid.UUID
    filename: str
    uploaded_at: datetime

    class Config:
        from_attributes = True


class FileDetailOut(FileOut):
    content: Optional[str] = None
