from fastapi import FastAPI
from app.api.endpoints.auth import auth_router
from app.api.endpoints.users import users_router

app = FastAPI(
    title="vPBX API",
    description="vPBX 시스템 관리를 위한 REST API",
    version="1.0.0"
)

# API 라우터 등록
app.include_router(
    auth_router, 
    prefix="/auth", 
    tags=["인증 API"]
)

app.include_router(
    users_router, 
    prefix="/users", 
    tags=["사용자 관리 API"]
)

@app.get("/")
async def root():
    return {
        "message": "vPBX API 서버에 오신 것을 환영합니다!",
        "docs_url": "/docs",
        "endpoints": {
            "auth": ["/auth/login", "/auth/logout", "/auth/verify"],
            "users": ["/users/add", "/users/delete", "/users/update"]
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 