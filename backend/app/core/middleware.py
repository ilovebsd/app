from fastapi import Request
from fastapi.responses import JSONResponse
import re

async def xss_protection_middleware(request: Request, call_next):
    try:
        body = await request.json()
        # XSS 패턴 검사
        if any(re.search(r'<script.*?>.*?</script>', str(value), re.I) 
               for value in body.values()):
            return JSONResponse(
                status_code=400,
                content={"detail": "잠재적인 XSS 공격이 감지되었습니다"}
            )
    except:
        pass
    response = await call_next(request)
    return response 