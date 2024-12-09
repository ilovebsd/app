from pydantic import BaseModel, validator
from typing import Optional
from datetime import datetime
import re

# 기본 사용자 모델
class UserBase(BaseModel):
    username: str

# 사용자 생성 스키마
class UserCreate(UserBase):
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

# 사용자 업데이트 스키마
class UserUpdate(BaseModel):
    password: Optional[str] = None
    userlevel: Optional[int] = None

    class Config:
        json_schema_extra = {
            "example": {
                "password": "NewPassword123!"
            }
        }

# 비밀번호 업데이트 요청 스키마
class PasswordUpdateRequest(BaseModel):
    username: str
    new_password: str

# 사용자 응답 스키마
class UserResponse(BaseModel):
    username: str
    userlevel: int
    onlogin: int

    class Config:
        from_attributes = True

# 데이터베이스 사용자 스키마
class UserInDB(UserBase):
    userlevel: int
    onlogin: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True 