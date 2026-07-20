# main.py — 진입점: 고객 의뢰를 받아 PM 에이전트를 돌린다.

import anthropic
from dotenv import load_dotenv

from pm_agent import run_pm


def main():
    load_dotenv()                 # .env 의 ANTHROPIC_API_KEY 를 환경변수로 로드
    client = anthropic.Anthropic()  # 키는 환경변수에서 자동으로 읽힘

    request = input("고객 의뢰를 입력하세요: ").strip()
    if not request:
        request = "할 일을 등록하고 완료 체크할 수 있는 간단한 웹 할일 관리 앱"

    print(f"\n[기획자] '{request}'\n         요구사항 정의를 시작합니다...\n")
    run_pm(client, request)
    print("\n[완료] output/ 폴더를 확인하세요.")


if __name__ == "__main__":
    main()