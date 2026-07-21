# company.py — AI 회사(오케스트레이터/매니저).
# 직원들을 모아 일을 조율한다. 얼굴(러너)은 이 회사에 '의뢰'만 넘긴다.

from agents.pm import PMAgent
from agents.designer import DesignerAgent

class Company:
    def __init__(self):
        self.pm = PMAgent()
        self.designer = DesignerAgent()
    def build(self, request: str) -> None:
        """고객 의뢰 한 줄 → 요구사항 → 디자인 (직원 협업 파이프라인)."""
        #1) 기획자
        print(f"\n[{self.pm.name}] '{request}'\n         요구사항 정의 시작...\n")
        req_path = self.pm.run(request)

        #2) 핸드오프
        requirements = open(req_path, encoding="utf-8").read()

        #3) 디자이너 -> html 목업
        print(f"\n[{self.designer.name}] 요구사항 받아 화면 목업 제작...\n")
        self.designer.run(requirements)

        print("\n[완료] output/ 확인 → requirements.md, design.html")