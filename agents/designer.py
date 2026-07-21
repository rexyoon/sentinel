# agents/designer.py — 디자이너(OpenAI). 이제 설정만 채우면 끝.

from agents.openai_agent import OpenAICompatibleAgent


class DesignerAgent(OpenAICompatibleAgent):
    name = "디자이너"
    model = "gpt-4o"  # 나중에 원하는 OpenAI/Codex 모델로
    system = """너는 작은 SI 회사의 디자이너다.
요구사항 정의서를 읽고, 그 앱의 첫 화면을 보여주는
'단일 파일 HTML 목업'(인라인 CSS 포함)을 만든다.
- 브라우저에서 바로 열리는 완결된 HTML 하나.
- 깔끔하고 현대적인 한국어 UI.
완성하면 save_document 도구로 design.html 에 저장하라."""
    output_path = "output/design.html"