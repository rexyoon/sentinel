# agents/developer.py — 개발자(Kimi/Moonshot).

from agents.openai_agent import OpenAICompatibleAgent
from agents.marketing import MOONSHOT_URL


class DeveloperAgent(OpenAICompatibleAgent):
    name = "개발자"
    model = "kimi-k2-0711-preview"
    base_url = MOONSHOT_URL
    api_key_env = "MOONSHOT_API_KEY"
    system = """너는 작은 SI 회사의 개발자다.
아래 요구사항 정의서를 읽고, 실제로 '동작하는' 최소 구현을 만든다.
- 단일 파일 HTML + 인라인 JS (외부 라이브러리 없이 브라우저에서 바로 동작).
- 목업이 아니라 핵심 기능이 실제로 작동하는 로직을 넣는다.
완성하면 save_document 도구로 app.html 에 저장하라."""
    output_path = "output/app.html"