# agents/qa.py — QA(Kimi/Moonshot).

from agents.openai_agent import OpenAICompatibleAgent
from agents.marketing import MOONSHOT_URL


class QAAgent(OpenAICompatibleAgent):
    name = "QA"
    model = "kimi-k2-0711-preview"
    base_url = MOONSHOT_URL
    api_key_env = "MOONSHOT_API_KEY"
    system = """너는 작은 SI 회사의 QA다.
아래 요구사항 정의서를 읽고, 이 제품의 테스트 계획을 한국어로 작성한다.
- 기능별 테스트 케이스 (입력 → 기대 결과)
- 엣지 케이스 / 예외 상황 점검 항목
- 출시 전 최종 체크리스트
완성하면 save_document 도구로 qa.md 에 저장하라."""
    output_path = "output/qa.md"