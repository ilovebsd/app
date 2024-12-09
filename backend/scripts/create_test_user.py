#!/usr/bin/env python3
import bcrypt
import psycopg2
import logging

# 로깅 설정
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# DB 연결 정보
DB_PARAMS = {
    "dbname": "ems",
    "user": "ssw",
    "password": "ssw",
    "host": "220.73.223.245",
    "port": "39998"
}

def create_test_user(username="admin", password="admin"):
    try:
        # 비밀번호 해시화
        password_bytes = password.encode('utf-8')
        hashed = bcrypt.hashpw(password_bytes, bcrypt.gensalt())
        hashed_password = hashed.decode('utf-8')
        
        logger.debug(f"Generated hash for '{password}': {hashed_password}")
        
        # DB 연결
        conn = psycopg2.connect(**DB_PARAMS)
        cur = conn.cursor()
        
        # 기존 사용자 삭제
        cur.execute("DELETE FROM table_statusaccount WHERE username = %s", (username,))
        logger.debug(f"Deleted existing user: {username}")
        
        # 새 사용자 생성
        cur.execute("""
            INSERT INTO table_statusaccount (username, password, userlevel, onlogin)
            VALUES (%s, %s, %s, %s)
        """, (username, hashed_password, 1, 0))
        
        conn.commit()
        logger.debug(f"Created new user: {username}")
        
        # 생성된 사용자 확인
        cur.execute("SELECT username, password FROM table_statusaccount WHERE username = %s", (username,))
        result = cur.fetchone()
        logger.debug(f"Verified user creation - Username: {result[0]}, Hash: {result[1]}")
        
    except Exception as e:
        logger.error(f"Error creating test user: {str(e)}")
        if 'conn' in locals():
            conn.rollback()
        raise
    finally:
        if 'cur' in locals():
            cur.close()
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    create_test_user()
    logger.info("Test user creation completed") 