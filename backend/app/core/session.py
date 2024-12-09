from datetime import datetime
from typing import Dict, Optional
import jwt
from fastapi import HTTPException, status

class SessionManager:
    def __init__(self):
        self.active_sessions: Dict[str, str] = {}  # username: token
        self.max_sessions_per_user = 1
        
    def add_session(self, username: str, token: str) -> bool:
        """새 세션 추가"""
        # 기존 세션이 있으면 제거
        if username in self.active_sessions:
            del self.active_sessions[username]
            
        self.active_sessions[username] = token
        return True
        
    def validate_session(self, username: str, token: str) -> bool:
        """세션 유효성 검증"""
        return (username in self.active_sessions and 
                self.active_sessions[username] == token)
                
    def remove_session(self, username: str) -> None:
        """세션 제거"""
        if username in self.active_sessions:
            del self.active_sessions[username]

session_manager = SessionManager() 