from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from jose import JWTError, jwt
from app.core.config import settings
from app.core.deps import get_current_user
from app.core.security import verify_password, create_access_token
from app.crud.account import get_account
from app.db.session import get_db
import logging

logger = logging.getLogger(__name__)
auth_router = APIRouter()

async def authenticate_user(db: AsyncSession, username: str, password: str):
    """사용자 인증"""
    user = await get_account(db, username)
    if not user:
        logger.warning(f"Login attempt with non-existent username: {username}")
        return False
    
    if not verify_password(password, user.password):
        logger.warning(f"Invalid password attempt for user: {username}")
        return False
    
    return user

@auth_router.post("/login")
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
):
    """로그인 처리"""
    logger.debug(f"Login attempt for user: {form_data.username}")
    user = await authenticate_user(db, form_data.username, form_data.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_access_token(user.username)
    logger.info(f"Login successful for user: {form_data.username}")
    return {"access_token": access_token, "token_type": "bearer"}

@auth_router.post("/logout")
async def logout(current_user = Depends(get_current_user)):
    """로그아웃 처리"""
    logger.info(f"Logout successful for user: {current_user.username}")
    return {"success": True, "message": "Successfully logged out"} 