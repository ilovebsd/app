from pydantic import BaseModel, EmailStr, validator
from typing import Optional
from datetime import datetime
import re

class AccountBase(BaseModel):
    username: str

class AccountCreate(AccountBase):
    password: str
    userlevel: int = 1

    @validator('password')
    def password_strength(cls, v):
        if len(v) < 8:
            raise ValueError('비밀번호는 최소 8자 이상이어야 합니다')
        if not re.search(r'[A-Z]', v):
            raise ValueError('비밀번호는 최소 1개의 대문자를 포함해야 합니다')
        if not re.search(r'[a-z]', v):
            raise ValueError('비밀번호는 최소 1개의 소문자를 포함해야 합니다')
        if not re.search(r'\d', v):
            raise ValueError('비밀번호는 최소 1개의 숫자를 포함해야 합니다')
        if not re.search(r'[!@#\$%\^&\*\(\),\.\?:{}|<>\-_]', v):
            raise ValueError('비밀번호는 최소 1개의 특수문자를 포함해야 합니다')
        return v

class AccountUpdate(BaseModel):
    password: Optional[str] = None
    userlevel: Optional[int] = None

class AccountInDB(AccountBase):
    id: int
    userlevel: int
    onlogin: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer" 