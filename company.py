# company.py — AI 회사(매니저). 직원들을 모아 조율한다.

from agents.pm import PMAgent
from agents.designer import DesignerAgent
from agents.marketing import MarketingAgent
from agents.admin import AdminAgent


class Company:
    def __init__(self):
        self.pm = PMAgent()
        # 요구사항을 받아 각자 산출물을 내는 직원들 (전부 Agent 인터페이스)
        self.staff = [DesignerAgent(), MarketingAgent(), AdminAgent()]

    def build(self, request: str) -> None:
        # 1) 기획자 → 요구사항 정의서
        print(f"\n[{self.pm.name}] '{request}'\n         요구사항 정의 시작...\n")
        req_path = self.pm.run(request)
        requirements = open(req_path, encoding="utf-8").read()

        # 2) 나머지 직원들에게 요구사항을 넘겨 병렬적으로 각자 작업.
        #    ★ 매니저는 누가 Claude/OpenAI/Kimi인지 몰라도 된다 — run() 만 부른다.
        for staff in self.staff:
            print(f"\n[{staff.name}] 요구사항 받아 작업 시작...\n")
            staff.run(requirements)

        print("\n[완료] output/ 확인 → requirements.md, design.html, marketing.md, summary.md")