from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.deps import get_current_user
from app.core.auth_handler import verify_password, create_access_token
from app.crud.user_crud import get_account
from app.db.db_config import get_db
from app.schemas.auth_schema import LoginRequest, TokenResponse
from app.core.security import (
    create_access_token, 
    verify_password, 
    password_validator,
    sanitize_input
)
from app.core.session import session_manager
import logging
import bcrypt

logger = logging.getLogger(__name__)
auth_router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

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

@auth_router.post("/login", response_model=TokenResponse)
async def login(
    login_data: LoginRequest,
    db: AsyncSession = Depends(get_db)
):
    """로그인 처리"""
    try:
        # 입력값 정제
        username = sanitize_input(login_data.username)
        password = sanitize_input(login_data.password)
        
        if not username or not password:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username and password are required"
            )
            
        # 사용자 확인 - 디버깅 로그 추가
        print(f"Attempting login for user: {username}")  # 디버깅
        user = await get_account(db, username)
        print(f"Found user: {user}")  # 디버깅
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials"
            )
            
        # 비밀번호 검증 - 디버깅 로그 추가
        is_valid = verify_password(password, user.password)
        print(f"Password verification result: {is_valid}")  # 디버깅
        
        if not is_valid:
            print("Invalid password")  # 디버깅
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials"
            )
            
        # 토큰 생성
        token = create_access_token(username)
        
        # 세션 등록
        session_manager.add_session(username, token)
        
        return {"access_token": token, "token_type": "bearer"}
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Login error: {str(e)}")  # 디버깅
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@auth_router.post("/logout")
async def logout(
    current_user: str = Depends(get_current_user)
):
    """로그아웃 처리"""
    try:
        session_manager.remove_session(current_user)
        return {"success": True, "message": "Successfully logged out"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@auth_router.get("/verify")
async def verify_token(current_user: str = Depends(get_current_user)):
    """토큰 검증"""
    return {"valid": True, "username": current_user} 