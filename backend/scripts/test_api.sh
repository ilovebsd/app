#!/bin/bash

# 색상 정의
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# API 엔드포인트 설정
BASE_URL="http://localhost:8000"

# 테스트 계정 정보 (실제 DB에 있는 계정으로 수정)
USERNAME="admin"    # DB에 있는 실제 사용자명
PASSWORD="admin"    # DB에 있는 실제 비밀번호
NEW_PASSWORD="newpass123"
WEAK_PASSWORD="123"
INVALID_PASSWORD="pass word"
SPECIAL_PASSWORD="pass!@#$"
LONG_PASSWORD="verylongpasswordover20characters"

# 함수: API 응답 코드 확인
check_response() {
    if [ $1 -eq $2 ]; then
        echo -e "${GREEN}성공${NC}"
    else
        echo -e "${RED}실패 (예상: $2, 실제: $1)${NC}"
        echo -e "Response: ${RESPONSE}"  # 실패 시 응답 출력
    fi
}

echo "=== API 테스트 시작 ==="

# 1. 정상 로그인 시도
echo -e "\n1. 정상 로그인 시도..."
RESPONSE=$(curl -s -X POST "${BASE_URL}/auth/login" \
     -H "Content-Type: application/x-www-form-urlencoded" \
     -d "username=${USERNAME}&password=${PASSWORD}")

# 토큰 한 번만 추출
TOKEN=$(echo $RESPONSE | jq -r .access_token)

if [ -n "$TOKEN" ]; then
    echo -e "${GREEN}로그인 성공 - 토큰 발급됨${NC}"
    echo "발급된 토큰: ${TOKEN}"
else
    echo -e "${RED}로그인 실패 - 토큰 없음${NC}"
    exit 1
fi

# 2. 토큰 검증 (한 번만 전송)
echo -e "\n2. 토큰 검증..."
RESPONSE=$(curl -s -X GET "${BASE_URL}/auth/verify" \
     -H "Authorization: Bearer ${TOKEN}")

echo "검증 응답: ${RESPONSE}"  # 검증 응답 확인
HTTP_CODE=${RESPONSE: -3}
check_response $HTTP_CODE 200

# 3. 사용자 정보 조회
echo -e "\n3. 사용자 정보 조회..."
RESPONSE=$(curl -s -w "%{http_code}" -X GET "${BASE_URL}/users/info" \
     -H "Authorization: Bearer ${TOKEN}")
HTTP_CODE=${RESPONSE: -3}
check_response $HTTP_CODE 200

# 4. 비밀번호 패턴 테스트
echo -e "\n=== 비밀번호 패턴 테스트 ==="

echo -e "\n4.1. 너무 짧은 비밀번호 (8자 미만)..."
RESPONSE=$(curl -s -w "%{http_code}" -X PUT "${BASE_URL}/users/update" \
     -H "Authorization: Bearer ${TOKEN}" \
     -H "Content-Type: application/x-www-form-urlencoded" \
     -d "username=${USERNAME}&new_password=${WEAK_PASSWORD}")
HTTP_CODE=${RESPONSE: -3}
check_response $HTTP_CODE 400

echo -e "\n4.2. 공백이 포함된 비밀번호..."
RESPONSE=$(curl -s -w "%{http_code}" -X PUT "${BASE_URL}/users/update" \
     -H "Authorization: Bearer ${TOKEN}" \
     -H "Content-Type: application/x-www-form-urlencoded" \
     -d "username=${USERNAME}&new_password=${INVALID_PASSWORD}")
HTTP_CODE=${RESPONSE: -3}
check_response $HTTP_CODE 400

echo -e "\n4.3. 특수문자가 포함된 비밀번호..."
RESPONSE=$(curl -s -w "%{http_code}" -X PUT "${BASE_URL}/users/update" \
     -H "Authorization: Bearer ${TOKEN}" \
     -H "Content-Type: application/x-www-form-urlencoded" \
     -d "username=${USERNAME}&new_password=${SPECIAL_PASSWORD}")
HTTP_CODE=${RESPONSE: -3}
check_response $HTTP_CODE 400

echo -e "\n4.4. 너무 긴 비밀번호 (20자 초과)..."
RESPONSE=$(curl -s -w "%{http_code}" -X PUT "${BASE_URL}/users/update" \
     -H "Authorization: Bearer ${TOKEN}" \
     -H "Content-Type: application/x-www-form-urlencoded" \
     -d "username=${USERNAME}&new_password=${LONG_PASSWORD}")
HTTP_CODE=${RESPONSE: -3}
check_response $HTTP_CODE 400

# 5. 올바른 비밀번호로 변경
echo -e "\n5. 올바른 비밀번호로 변경..."
RESPONSE=$(curl -s -w "%{http_code}" -X PUT "${BASE_URL}/users/update" \
     -H "Authorization: Bearer ${TOKEN}" \
     -H "Content-Type: application/x-www-form-urlencoded" \
     -d "username=${USERNAME}&new_password=${NEW_PASSWORD}")
HTTP_CODE=${RESPONSE: -3}
check_response $HTTP_CODE 200

# 6. 새 비밀번호로 로그인
echo -e "\n6. 새 비밀번호로 로그인..."
RESPONSE=$(curl -s -X POST "${BASE_URL}/auth/login" \
     -H "Content-Type: application/x-www-form-urlencoded" \
     -d "username=${USERNAME}&password=${NEW_PASSWORD}")
NEW_TOKEN=$(echo $RESPONSE | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)

if [ -n "$NEW_TOKEN" ]; then
    echo -e "${GREEN}새 비밀번호로 로그인 성공${NC}"
    TOKEN=$NEW_TOKEN
else
    echo -e "${RED}새 비밀번호로 로그인 실패${NC}"
    exit 1
fi

# 7. 보안 테스트
echo -e "\n=== 보안 테스트 ==="

echo -e "\n7.1. 잘못된 계정으로 로그인 시도..."
RESPONSE=$(curl -s -w "%{http_code}" -X POST "${BASE_URL}/auth/login" \
     -H "Content-Type: application/x-www-form-urlencoded" \
     -d "username=wrong&password=wrong")
HTTP_CODE=${RESPONSE: -3}
check_response $HTTP_CODE 401

echo -e "\n7.2. XSS 공격 시도..."
RESPONSE=$(curl -s -w "%{http_code}" -X POST "${BASE_URL}/auth/login" \
     -H "Content-Type: application/x-www-form-urlencoded" \
     -d "username=<script>alert(1)</script>&password=test")
HTTP_CODE=${RESPONSE: -3}
check_response $HTTP_CODE 401

echo -e "\n7.3. SQL Injection 시도..."
RESPONSE=$(curl -s -w "%{http_code}" -X POST "${BASE_URL}/auth/login" \
     -H "Content-Type: application/x-www-form-urlencoded" \
     -d "username=admin'--&password=test")
HTTP_CODE=${RESPONSE: -3}
check_response $HTTP_CODE 401

# 8. 원래 비밀번호로 복구
echo -e "\n8. 원래 비밀번호로 복구..."
RESPONSE=$(curl -s -w "%{http_code}" -X PUT "${BASE_URL}/users/update" \
     -H "Authorization: Bearer ${TOKEN}" \
     -H "Content-Type: application/x-www-form-urlencoded" \
     -d "username=${USERNAME}&new_password=${PASSWORD}")
HTTP_CODE=${RESPONSE: -3}
check_response $HTTP_CODE 200

echo -e "\n현재 계정 정보:"
echo -e "사용자명: ${USERNAME}"
echo -e "비밀번호: ${PASSWORD}"
echo -e "\n다음 테스트 시 위 계정 정보로 로그인하세요."

# 9. 로그아웃
echo -e "\n9. 로그아웃..."
RESPONSE=$(curl -s -w "%{http_code}" -X POST "${BASE_URL}/auth/logout" \
     -H "Authorization: Bearer ${TOKEN}")
HTTP_CODE=${RESPONSE: -3}
check_response $HTTP_CODE 200

# 10. 로그아웃 상태에서 보호된 엔드포인트 접근
echo -e "\n10. 로그아웃 상태에서 보호된 엔드포인트 접근..."
RESPONSE=$(curl -s -w "%{http_code}" -X GET "${BASE_URL}/users/info" \
     -H "Authorization: Bearer ${TOKEN}")
HTTP_CODE=${RESPONSE: -3}
check_response $HTTP_CODE 401

# 11. 다양한 로그인 실패 케이스
echo -e "\n=== 로그인 실패 케이스 테스트 ==="

echo -e "\n11.1. 존재하지 않는 사용자로 로그인 시도..."
RESPONSE=$(curl -s -w "%{http_code}" -X POST "${BASE_URL}/auth/login" \
     -H "Content-Type: application/x-www-form-urlencoded" \
     -d "username=nonexistent&password=${PASSWORD}")
HTTP_CODE=${RESPONSE: -3}
check_response $HTTP_CODE 401

echo -e "\n11.2. 잘못된 비밀번호로 로그인 시도..."
RESPONSE=$(curl -s -w "%{http_code}" -X POST "${BASE_URL}/auth/login" \
     -H "Content-Type: application/x-www-form-urlencoded" \
     -d "username=${USERNAME}&password=wrongpass")
HTTP_CODE=${RESPONSE: -3}
check_response $HTTP_CODE 401

echo -e "\n11.3. 빈 사용자명으로 로그인 시도..."
RESPONSE=$(curl -s -w "%{http_code}" -X POST "${BASE_URL}/auth/login" \
     -H "Content-Type: application/x-www-form-urlencoded" \
     -d "username=&password=${PASSWORD}")
HTTP_CODE=${RESPONSE: -3}
check_response $HTTP_CODE 422

echo -e "\n11.4. 빈 비밀번호로 로그인 시도..."
RESPONSE=$(curl -s -w "%{http_code}" -X POST "${BASE_URL}/auth/login" \
     -H "Content-Type: application/x-www-form-urlencoded" \
     -d "username=${USERNAME}&password=")
HTTP_CODE=${RESPONSE: -3}
check_response $HTTP_CODE 422

echo -e "\n11.5. 공백 문자만 있는 사용자명으로 로그인 시도..."
RESPONSE=$(curl -s -w "%{http_code}" -X POST "${BASE_URL}/auth/login" \
     -H "Content-Type: application/x-www-form-urlencoded" \
     -d "username=   &password=${PASSWORD}")
HTTP_CODE=${RESPONSE: -3}
check_response $HTTP_CODE 422

echo -e "\n11.6. 공백 문자만 있는 비밀번호로 로그인 시도..."
RESPONSE=$(curl -s -w "%{http_code}" -X POST "${BASE_URL}/auth/login" \
     -H "Content-Type: application/x-www-form-urlencoded" \
     -d "username=${USERNAME}&password=   ")
HTTP_CODE=${RESPONSE: -3}
check_response $HTTP_CODE 422

echo -e "\n=== 테스트 완료 ===" 