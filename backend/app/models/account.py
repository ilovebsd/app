from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Account(Base):
    __tablename__ = "table_statusaccount"
    
    username = Column(String(32), primary_key=True)
    password = Column(String(60))
    userlevel = Column(Integer)
    onlogin = Column(Integer)

    def __repr__(self):
        return f"Account(username={self.username}, userlevel={self.userlevel}, onlogin={self.onlogin})" 