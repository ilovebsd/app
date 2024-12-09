from fastapi import APIRouter

router = APIRouter()

@router.get("/health")
async def health_check():
    return {"status": "ok"}

@router.get("/health/db")
async def db_health_check():
    # DB 연결 확인 로직 추가
    return {"status": "ok"} 