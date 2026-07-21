# agents/admin.py — 행정 담당(Kimi/Moonshot).
from agents.openai_agent import OpenAICompatibleAgent
from agents.marketing import MOONSHOT_URL
class AdminAgent(OpenAICompatibleAgent):
    name = "행정"
    model = "kimi-k2-0711-preview"
    base_url = MOONSHOT_URL
    api_key_env = "MOONSHOT_API_KEY"
    system = """너는 작은 SI 회사의 행정 담당이다.
아래 요구사항 정의서를 읽고, 프로젝트 착수 요약서를 한국어로 작성한다.
- 프로젝트명 / 한 줄 소개
- 작업 범위 요약
- 예상 산출물 목록
- 대략적 단계와 일정(주 단위)
완성하면 save_document 도구로 summary.md 에 저장하라."""
    output_path = "output/summary.md"