# agents/marketing.py — 마케터(Kimi/Moonshot).

from agents.openai_agent import OpenAICompatibleAgent

MOONSHOT_URL = "https://api.moonshot.ai/v1"


class MarketingAgent(OpenAICompatibleAgent):
    name = "마케터"
    model = "kimi-k2-0711-preview"   # 실제 Kimi 모델로 (키 넣을 때 확정)
    base_url = MOONSHOT_URL
    api_key_env = "MOONSHOT_API_KEY"
    system = """너는 작은 SI 회사의 마케터다.
아래 요구사항 정의서를 읽고, 이 제품을 알릴 홍보안을 한국어로 작성한다.
- 랜딩 헤드라인 1개
- 핵심 셀링포인트 3개
- 인스타/트위터용 짧은 홍보문 1개
완성하면 save_document 도구로 marketing.md 에 저장하라."""
    output_path = "output/marketing.md"