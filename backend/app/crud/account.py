from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import IntegrityError
from ..models.account import Account
from ..core.security import get_password_hash
import logging

logger = logging.getLogger(__name__)

async def get_account(db: AsyncSession, username: str):
    """사용자 계정 조회"""
    try:
        query = select(Account).where(Account.username == username)
        result = await db.execute(query)
        return result.scalar_one_or_none()
    except Exception as e:
        logger.error(f"Error fetching account for {username}: {str(e)}")
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