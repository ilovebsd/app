from pydantic import BaseModel, constr

class UserUpdate(BaseModel):
    password: str

    class Config:
        json_schema_extra = {
            "example": {
                "password": "NewPassword123!"
            }
        }