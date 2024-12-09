from datetime import datetime, timedelta
from jose import jwt, JWTError
import bcrypt
import logging
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer

# JWT 설정
SECRET_KEY = "your-secret-key"  # 실제 운영환경에서는 환경변수로 관리
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

logger = logging.getLogger(__name__)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

async def get_current_user(token: str = Depends(oauth2_scheme)):
    print(f"Validating token: {token}")  # 디버깅용
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        print(f"Decoded username: {username}")  # 디버깅용
        if username is None:
            raise HTTPException(status_code=401)
        return username
    except JWTError as e:
        print(f"JWT Error: {e}")  # 디버깅용
        raise HTTPException(status_code=401)

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
        return bcrypt.checkpw(
            plain_password.encode('utf-8'),
            hashed_password.encode('utf-8')
        )
    except Exception as e:
        print(f"Password verification error: {e}")
        return False