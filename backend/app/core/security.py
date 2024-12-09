import bcrypt
import hashlib
import logging
import re
import unicodedata
from typing import Tuple
from datetime import datetime, timedelta
from jose import JWTError, jwt
from fastapi import HTTPException, status
from passlib.context import CryptContext

logger = logging.getLogger(__name__)

# 비밀번호 해싱
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT 설정
SECRET_KEY = "your-secret-key"  # 실제 운영에서는 환경변수로 관리
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

class PasswordValidator:
    def __init__(self):
        self.common_patterns = [
            r'qwerty', r'asdfgh', r'zxcvbn', r'password', r'admin', 
            r'123456', r'abcdef'
        ]
        self.consecutive_numbers = r'\d{3,}'  # 3개 이상 연속된 숫자
        
    def validate(self, password: str) -> Tuple[bool, str]:
        """비밀번호 유효성 검증"""
        try:
            # 기본 길이 검증
            if len(password) < 8:
                return False, "비밀번호는 최소 8자 이상이어야 합니다"
            if len(password) > 20:
                return False, "비밀번호는 20자를 초과할 수 없습니다"
                
            # 공백 검사
            if ' ' in password:
                return False, "비밀번호에 공백을 포함할 수 없습니다"
                
            # 문자 종류 검증
            if not re.search(r'[A-Z]', password):
                return False, "비밀번호는 최소 1개의 대문자를 포함해야 합니다"
            if not re.search(r'[a-z]', password):
                return False, "비밀번호는 최소 1개의 소문자를 포함해야 합니다"
            if not re.search(r'\d', password):
                return False, "비밀번호는 최소 1개의 숫자를 포함해야 합니다"
            if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
                return False, "비밀번호는 최소 1개의 특수문자를 포함해야 합니다"
                
            # 패턴 검사
            if re.search(self.consecutive_numbers, password):
                return False, "연속된 숫자는 사용할 수 없습니다"
                
            # 일반적인 패턴 검사
            lower_password = password.lower()
            for pattern in self.common_patterns:
                if pattern in lower_password:
                    return False, "일반적인 패턴이 포함된 비밀번호는 사용할 수 없습니다"
                    
            return True, ""
            
        except Exception as e:
            return False, f"비밀번호 검증 중 오류 발생: {str(e)}"

def create_access_token(username: str) -> str:
    """JWT 토큰 생성"""
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode = {"sub": username, "exp": expire}
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def decode_token(token: str) -> dict:
    """JWT 토큰 디코딩"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )

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

def get_password_hash(password: str) -> str:
    """비밀번호 해싱"""
    return pwd_context.hash(password)

def sanitize_input(value: str) -> str:
    """입력값 정제"""
    if not value:
        return value
        
    # Unicode 정규화
    value = unicodedata.normalize('NFKC', str(value))
    
    # Null bytes 제거
    value = value.replace('\0', '')
    
    # 위험한 문자 제거
    value = re.sub(r'[<>\'";]', '', value)
    
    return value.strip()

# 전역 인스턴스 생성
password_validator = PasswordValidator()