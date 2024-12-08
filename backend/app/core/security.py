from datetime import datetime, timedelta
from jose import jwt
import bcrypt
import logging

# JWT 설정
SECRET_KEY = "your-secret-key-here"  # 실제 운영환경에서는 환경변수로 관리
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

logger = logging.getLogger(__name__)

def create_access_token(username: str) -> str:
    """JWT 토큰 생성"""
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode = {
        "sub": username,
        "exp": expire
    }
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_password_hash(password: str) -> str:
    """비밀번호 해싱"""
    try:
        hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        return hashed.decode('utf-8')
    except Exception as e:
        logger.error(f"Error during password hashing: {str(e)}")
        raise

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """비밀번호 검증"""
    try:
        result = bcrypt.checkpw(
            plain_password.encode('utf-8'), 
            hashed_password.encode('utf-8')
        )
        if not result:
            logger.warning("Password verification failed")
        return result
    except Exception as e:
        logger.error(f"Password verification error: {str(e)}")
        return False