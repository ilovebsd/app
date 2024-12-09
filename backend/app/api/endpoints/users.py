from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.deps import get_current_user
from app.crud.user_crud import update_password
from app.db.db_config import get_db
from app.models.user_model import Account
from app.schemas.user_schema import UserUpdate, UserResponse
import re
import logging

logger = logging.getLogger(__name__)
users_router = APIRouter()

def validate_password(password: str) -> tuple[bool, str]:
    """비밀번호 유효성 검사"""
    if len(password) < 8:
        return False, "비밀번호는 최소 8자 이상이어야 합니다"
    if len(password) > 20:
        return False, "비밀번호는 20자를 초과할 수 없습니다"
    if ' ' in password:
        return False, "비밀번호에 공백을 포함할 수 없습니다"
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return False, "비밀번호는 최소 1개의 특수문자를 포함해야 합니다"
    return True, ""

@users_router.get("/info", response_model=UserResponse)
async def get_user_info(current_user: Account = Depends(get_current_user)):
    """현재 로그인한 사용자 정보 조회"""
    return {
        "username": current_user.username,
        "userlevel": current_user.userlevel,
        "onlogin": current_user.onlogin
    }

@users_router.put("/update")
async def update_user(
    user_update: UserUpdate,
    current_user: Account = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """사용자 비밀번호 업데이트"""
    try:
        # 비밀번호 유효성 검사
        is_valid, error_message = validate_password(user_update.password)
        if not is_valid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error_message
            )
            
        result = await update_password(db, current_user.username, user_update.password)
        if result:
            logger.info(f"Password updated successfully for user: {current_user.username}")
            return {
                "status": "success",
                "message": "비밀번호가 성공적으로 변경되었습니다."
            }
            
        logger.warning(f"Password update failed - user not found: {current_user.username}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="사용자를 찾을 수 없습니다."
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Password update error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )