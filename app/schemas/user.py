from datetime import datetime

from pydantic import BaseModel, EmailStr, ConfigDict, field_validator
from typing import Optional
import re

class UserBase(BaseModel):
    name: str
    email: EmailStr
    about: Optional[str] = None

class UserCreate(UserBase):
    password: str

    @field_validator('password')
    def password_strength(cls, v):
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")
        if not re.search(r'[A-Z]', v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not re.search(r'[a-z]', v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not re.search(r'[0-9]', v):
            raise ValueError("Password must contain at least one number")
        return v


class UserLogIn(BaseModel):
    email: EmailStr
    password: str

class UserOut(UserBase):
    id: int
    last_login: datetime
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class UserOtherOut(BaseModel):
    id: int
    name: str

    model_config = ConfigDict(from_attributes=True)