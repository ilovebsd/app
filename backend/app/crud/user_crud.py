from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import update
from sqlalchemy.exc import IntegrityError
from ..models.user_model import Account
from ..core.auth_handler import get_password_hash
import logging
import bcrypt

logger = logging.getLogger(__name__)

async def get_account(db: AsyncSession, username: str):
    """사용자 계정 조회"""
    try:
        print(f"Querying DB for username: {username}")
        stmt = select(Account).where(Account.username == username)
        result = await db.execute(stmt)
        user = result.scalar_one_or_none()
        
        if user:
            # 사용자 객체의 모든 속성 출력 - id 제거
            print(f"Found user details:")
            print(f"  Username: {user.username}")
            print(f"  Password: {user.password}")  # 실제 환경에서는 비밀번호 출력 금지
            print(f"  Userlevel: {user.userlevel}")
            print(f"  Onlogin: {user.onlogin}")
        
        return user
        
    except Exception as e:
        print(f"DB query error: {str(e)}")
        raise

async def create_account(db: AsyncSession, username: str, password: str, userlevel: int = 1):
    """새 계정 생성"""
    try:
        hashed_password = get_password_hash(password)
        account = Account(
            username=username,
            password=hashed_password,
            userlevel=userlevel,
            onlogin=0
        )
        db.add(account)
        await db.commit()
        await db.refresh(account)
        logger.info(f"Account created successfully: {username}")
        return account
    except IntegrityError:
        logger.warning(f"Account creation failed - username already exists: {username}")
        await db.rollback()
        raise
    except Exception as e:
        logger.error(f"Error creating account: {str(e)}")
        await db.rollback()
        raise

async def update_account(db: AsyncSession, account: Account, update_data: dict):
    """계정 정보 업데이트"""
    try:
        if "password" in update_data:
            update_data["password"] = get_password_hash(update_data["password"])

        for key, value in update_data.items():
            setattr(account, key, value)

        db.add(account)
        await db.commit()
        await db.refresh(account)
        logger.info(f"Account updated successfully: {account.username}")
        return account
    except Exception as e:
        logger.error(f"Error updating account: {str(e)}")
        await db.rollback()
        raise

async def delete_account(db: AsyncSession, username: str):
    """계정 삭제"""
    try:
        account = await get_account(db, username)
        if account:
            await db.delete(account)
            await db.commit()
            logger.info(f"Account deleted successfully: {username}")
            return True
        return False
    except Exception as e:
        logger.error(f"Error deleting account: {str(e)}")
        await db.rollback()
        raise

async def update_password(db: AsyncSession, username: str, new_password: str):
    """비밀번호 업데이트"""
    try:
        # 1. 사용자 존재 여부 확인
        account = await get_account(db, username)
        if not account:
            logger.warning(f"Password update failed - user not found: {username}")
            return None
            
        # 2. 비밀번호 해시화
        hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
        
        # 3. 업데이트 쿼리 실행
        query = update(Account).where(Account.username == username).values(
            password=hashed_password.decode('utf-8')
        )
        await db.execute(query)
        await db.commit()
        
        logger.info(f"Password updated successfully: {username}")
        return True
        
    except Exception as e:
        logger.error(f"Error updating password: {str(e)}")
        await db.rollback()
        raise