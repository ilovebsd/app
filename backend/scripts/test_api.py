#!/usr/bin/env python3
import requests
import json
import sys
from colorama import Fore, Style, init

init()

BASE_URL = "http://localhost:8000"
USERNAME = "admin"
PASSWORD = "admin"

def print_result(message, success, response):
    """테스트 결과와 응답 내용 상세 출력"""
    status = "성공" if success else "실패"
    color = Fore.GREEN if success else Fore.RED

    print(f"\n{message}")
    print(f"상태: {color}{status}{Style.RESET_ALL}")
    print(f"응답 코드: {response.status_code}")
    print(f"요청 URL: {response.request.url}")
    print(f"요청 바디: {response.request.body}")
    print(f"응답 내용: {response.text}")
    print("-" * 50)

def test_api():
    session = requests.Session()
    session.headers.update({"Content-Type": "application/json"})

    print("\n=== API 테스트 시작 ===")

    # 먼저 정상 로그인 시도
    print("\n=== 1. 정상 로그인 테스트 ===")
    login_data = {"username": USERNAME, "password": PASSWORD}
    response = session.post(f"{BASE_URL}/auth/login", json=login_data)
    print_result("1.1 정상 로그인", response.status_code == 200, response)

    # 그 다음 실패 케이스 테스트
    print("\n=== 2. 로그인 실패 테스트 ===")
    failed_login_cases = {
        "존재하지 않는 사용자": {"username": "nonexistent", "password": "test123"},
        "잘못된 비밀번호": {"username": USERNAME, "password": "wrongpass"},
        "빈 사용자명": {"username": "", "password": PASSWORD},
        "빈 비밀번호": {"username": USERNAME, "password": ""},
        "공백 사용자명": {"username": "   ", "password": PASSWORD},
        "공백 비밀번호": {"username": USERNAME, "password": "   "},
        "특수문자 사용자명": {"username": "admin!@#", "password": PASSWORD},
        "매우 긴 사용자명": {"username": "a" * 100, "password": PASSWORD}
    }

    for case_name, test_data in failed_login_cases.items():
        response = session.post(f"{BASE_URL}/auth/login", json=test_data)
        print_result(f"2.1 로그인 실패 테스트: {case_name}", 
                    response.status_code in [400, 401], response)

if __name__ == "__main__":
    try:
        test_api()
    except Exception as e:
        print(f"{Fore.RED}오류 발생: {str(e)}{Style.RESET_ALL}")
        sys.exit(1) 