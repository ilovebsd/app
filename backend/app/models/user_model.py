from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Account(Base):
    __tablename__ = "table_statusaccount"
    
    username = Column(String(32), primary_key=True, index=True)
    password = Column(String(128))
    userlevel = Column(Integer)  # 1: 사용자, 2: vPBX DB 네임
    onlogin = Column(Integer)    # 0: 로그오프, 1: 로그인