from fastapi import APIRouter, Depends, HTTPException, status, Body
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Any
from pydantic import BaseModel
from app.db.session import get_db
from app.core.deps import get_current_user
from app.core.security import verify_password
from app.crud.account import get_account, create_account, update_account, delete_account
from app.models.account import Account
import logging

# 로깅 설정
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

users_router = APIRouter()

class UserCreate(BaseModel):
    username: str
    password: str
    userlevel: int

class UserDelete(BaseModel):
    username: str

class PasswordUpdate(BaseModel):
    old_password: str
    new_password: str

@users_router.post("/add")
async def add_user(
    user_in: UserCreate,
    token: str = Depends(oauth2_scheme),
    current_user: Account = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """새로운 사용자 추���"""
    logger.debug(f"User creation attempt by {current_user.username}")
    
    if await get_account(db, username=user_in.username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="이미 존재하는 사용자명입니다."
        )
    
    user = await create_account(db, user_in)
    return {
        "status": "success",
        "message": f"사용자 '{user.username}'가 생성되었습니다.",
        "username": user.username,
        "userlevel": user.userlevel
    }

@users_router.delete("/delete")
async def delete_user(
    request: UserDelete,
    token: str = Depends(oauth2_scheme),
    current_user: Account = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """사용자 삭제"""
    user_to_delete = await get_account(db, request.username)
    if not user_to_delete:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"사용자 '{request.username}'를 찾을 수 없습니다."
        )
    
    if user_to_delete.username == current_user.username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="자기 자신의 계정은 삭제할 수 없습니다."
        )
    
    await delete_account(db, user_to_delete)
    return {
        "status": "success",
        "message": f"사용자 '{request.username}'가 삭제되었습니다."
    }

@users_router.put("/update")
async def update_password(
    password: str = Body(...),
    db: AsyncSession = Depends(get_db),
    current_user: Account = Depends(get_current_user)
):
    """비밀번호 변경"""
    if not verify_password(password, current_user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="현재 비밀번호가 일치하지 않습니다."
        )
    
    if len(password) < 8:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="비밀번호는 최소 8자 이상이어야 합니다."
        )
    
    await update_account(db, current_user, {"password": password})
    return {
        "status": "success",
        "message": "비밀번호가 변경되었습니다."
    }