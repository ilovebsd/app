from fastapi import Request
from fastapi.responses import JSONResponse
import re
import json
import logging

logger = logging.getLogger(__name__)

async def xss_protection_middleware(request: Request, call_next):
    try:
        body = await request.json()
        # XSS 패턴 검사
        if any(re.search(r'<script.*?>.*?</script>', str(value), re.I) 
               for value in body.values()):
            logger.warning("XSS 공격 시도가 감지되었습니다")
            return JSONResponse(
                status_code=400,
                content={"detail": "잠재적인 XSS 공격이 감지되었습니다"}
            )
    except json.JSONDecodeError:
        # JSON 파싱 실패는 정상적인 경우일 수 있음 (예: form-data)
        pass
    except Exception as e:
        # 예상치 못한 오류는 로깅
        logger.error(f"미들웨어 처리 중 오류 발생: {str(e)}")
        pass
    
    response = await call_next(request)
    return response 