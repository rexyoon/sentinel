# runners/console.py — 터미널 얼굴. 사람과 입출력만 담당, 조율은 회사에 맡긴다.

from dotenv import load_dotenv

from company import Company


def main():
    load_dotenv()  # .env 의 API 키들 로드

    request = input("고객 의뢰를 입력하세요: ").strip()
    if not request:
        request = "할 일을 등록하고 완료 체크할 수 있는 간단한 웹 할일 관리 앱"

    company = Company()   # 회사를 차리고
    company.build(request)  # 의뢰를 넘긴다 — 나머지는 회사가 알아서