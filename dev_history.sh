#!/bin/bash

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 기본값 설정
DAYS=7
EXCLUDE_PATHS=""

# 이전 리포트 파일 정리
cleanup_reports() {
    find . -name "git_status_report_*.txt" -type f -mtime +1 -delete
    find . -name "project_status_report_*.txt" -type f -mtime +1 -delete
}

# 스크립트 시작 시 정리
cleanup_reports

# 기본 Git 무시 패턴 수정
DEFAULT_IGNORE_PATTERNS=(
    "__pycache__"
    "\.pyc$"
    "venv"
    "env"
    "node_modules"
    "dist"
    "build"
    "\.log$"
    "\.lock$"
    "\.env"
    "coverage"
    "\.git"
    "\.cursorrules"
    "\.code-workspace"
    "\.vscode"
    "git_status_report_.*\.txt"
    "project_status_report_.*\.txt"
)

# 사용법 출력 함수
print_usage() {
    echo "사용법: $0 [옵션]"
    echo "옵션:"
    echo "  -e, --exclude   제외할 경로들 (공백으로 구분)"
    echo "  -d, --days      분석할 기간 (일) (기본값: 7)"
    echo "  -h, --help      도움말 출력"
    echo
    echo "예시:"
    echo "  $0 --exclude 'tests docs'"
    echo "  $0 --exclude 'tests' --days 14"
}

# 명령행 인자 파싱
while [[ $# -gt 0 ]]; do
    case $1 in
        -e|--exclude)
            EXCLUDE_PATHS="$2"
            shift 2
            ;;
        -d|--days)
            DAYS="$2"
            shift 2
            ;;
        -h|--help)
            print_usage
            exit 0
            ;;
        *)
            echo "알 수 없는 옵션: $1"
            print_usage
            exit 1
            ;;
    esac
done

# 제외 패턴 생성
IGNORE_PATTERNS=("${DEFAULT_IGNORE_PATTERNS[@]}")
if [ ! -z "$EXCLUDE_PATHS" ]; then
    for path in $EXCLUDE_PATHS; do
        IGNORE_PATTERNS+=("$path")
    done
fi

# 무시 패턴을 문자열로 변환
IGNORE_STRING=$(IFS='|'; echo "${IGNORE_PATTERNS[*]}")

# 파일 패턴 수정
FILE_PATTERN="(\.py|\.sql|\.ts|\.tsx|\.js|\.jsx|\.css|\.scss|\.sh)$"

echo -e "${BLUE}=== 프로젝트 상태 분석 ===${NC}"
echo -e "${YELLOW}제외 경로: ${EXCLUDE_PATHS:-없음}${NC}\n"

# Git 저장소 분석
echo -e "${GREEN}[1. Git 저장소 상태]${NC}"
echo -e "${YELLOW}현재 브랜치:${NC}"
git branch -v

echo -e "\n${YELLOW}Git 상태:${NC}"
# 수정된 파일만 표시 (삭제된 파일 제외)
git status -s | grep "^.M\|^??" | grep -v -E "$IGNORE_STRING" || true

echo -e "\n${YELLOW}최근 ${DAYS}일간의 커밋 이력:${NC}"
git log --oneline --since="${DAYS} days ago" || true

# 프로젝트 구조
echo -e "\n${GREEN}[2. 프로젝트 구조]${NC}"
if command -v tree &> /dev/null; then
    tree -L 3 \
        -I "git_status_report_*|project_status_report_*|__pycache__|*.pyc|venv|node_modules|dist|build|coverage|.git|.vscode" \
        --noreport \
        --prune \
        --gitignore
else
    find . -maxdepth 3 -type f | 
    grep -v -E "$IGNORE_STRING" | 
    grep -E "$FILE_PATTERN" || true
fi

# 변경된 파일 분석
echo -e "\n${GREEN}[3. 주요 파일 변경 이력]${NC}"

# 현재 작업 디렉토리의 변경사항 가져오기
current_changes=$(git status -s | grep "^.M\|^??" | awk '{print $2}' | grep -v -E "$IGNORE_STRING" || true)

# Git에서 추적 중인 파일들 가져오기
tracked_files=$(git ls-tree -r HEAD --name-only | grep -v -E "$IGNORE_STRING" || true)

# 최근 커밋에서 변경된 파일들 가져오기
changed_files=$(git diff --name-only HEAD~1 HEAD 2>/dev/null | grep -v -E "$IGNORE_STRING" || true)

# 모든 파일 목록 생성 (중복 제거)
all_files=$(echo -e "${current_changes}\n${tracked_files}\n${changed_files}" | sort -u)

# 각 파일의 변경 이력 출력
if [ ! -z "$all_files" ]; then
    for file in $all_files; do
        if [ -f "$file" ]; then
            echo -e "\n${YELLOW}[$file] 변경 이력:${NC}"
            echo "----------------------------------------"
            # 현재 변경사항 표시
            if git status -s "$file" | grep -q "^.M"; then
                echo "현재 수정된 파일"
                echo -e "\n[현재 변경 내용]"
                git diff "$file" | grep -E "^(\+|\-)" | head -n 5 || true
            fi
            # Git 이력 표시
            git log -1 --pretty=format:"%h - %an, %ar : %s" -- "$file" || true
            echo "----------------------------------------"
        fi
    done
else
    echo "변경된 파일이 없습니다."
fi

# 커밋 통계
echo -e "\n${GREEN}[4. 커밋 통계]${NC}"
echo -e "${YELLOW}파일별 변경 횟수 (상위 5개):${NC}"
(git log --name-only --pretty=format: | 
    grep -E "$FILE_PATTERN" | 
    grep -v -E "$IGNORE_STRING" | 
    grep -v "^$" | 
    sort | uniq -c | sort -nr | 
    head -n 5) || echo "아직 커밋된 파일이 없습니다."

# 요약 리포트 생성
report_file="git_status_report_$(date '+%Y%m%d_%H%M%S').txt"
{
    echo "=== vPBX 프로젝트 Git 상태 리포트 ==="
    echo "생성 일시: $(date '+%Y-%m-%d %H:%M:%S')"
    echo "분석 기간: 최근 $DAYS 일"
    echo "제외 경로: ${EXCLUDE_PATHS:-없음}"
    
    echo -e "\n1. 현재 브랜치:"
    git branch -v
    
    echo -e "\n2. 최근 커밋:"
    git log --oneline -n 5 || true
    
    echo -e "\n3. 변경된 파일:"
    git status -s | grep -v -E "$IGNORE_STRING" | grep -E "$FILE_PATTERN" || true
    
    echo -e "\n4. 파일별 변경 횟수 (상위 5개):"
    git log --pretty=format: --name-only | grep -v -E "$IGNORE_STRING" | grep -E "$FILE_PATTERN" | sort | uniq -c | sort -rn | head -n 5 || true
    
} > "$report_file"

echo -e "\n${BLUE}Git 상태 리포트가 ${report_file}에 저장되었습니다.${NC}"

# 개발 방향성 제안
echo -e "\n${GREEN}[5. 개발 방향성 제안]${NC}"
echo "최근 ${DAYS}일간의 변경 패턴을 기준으로 다음 작업을 제안합니다:"

most_changed_dirs=$(git log --since="${DAYS} days ago" --name-only --pretty=format: | 
    grep -E "$FILE_PATTERN" |
    grep -v -E "$IGNORE_STRING" |
    awk -F/ '{print ($1=="cursorai.sh" ? "." : $1)}' |
    sort | uniq -c | sort -nr |
    awk '{print "- " ($2=="." ? "최상위" : $2) " 영역: " $1 "개의 변경사항"}')

echo -e "${YELLOW}주요 작업 영역:${NC}"
if [ ! -z "$most_changed_dirs" ]; then
    echo "$most_changed_dirs"
else
    echo "최근 변경된 작업 영역이 없습니다."
fi