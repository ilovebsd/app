from pydantic import BaseModel

class UserResponse(BaseModel):
    username: str
    userlevel: int
    onlogin: int

    class Config:
        from_attributes = True

class PasswordUpdateRequest(BaseModel):
    username: str
    new_password: str 