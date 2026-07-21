# agents/designer.py — 디자이너: 요구사항 → HTML 목업. 두뇌=OpenAI.

import json

from openai import OpenAI

from agents.base import Agent
from tools import save_document

MODEL = "gpt-4o"  # 나중에 원하는 OpenAI/Codex 모델로 교체

DESIGNER_SYSTEM = """너는 작은 SI 회사의 디자이너다.
요구사항 정의서를 읽고, 그 앱의 첫 화면을 보여주는
'단일 파일 HTML 목업'(인라인 CSS 포함)을 만든다.
- 브라우저에서 바로 열리는 완결된 HTML 하나.
- 깔끔하고 현대적인 한국어 UI.
완성하면 save_design 도구로 design.html 에 저장하라."""

SAVE_DESIGN_TOOL = {
    "type": "function",
    "function": {
        "name": "save_design",
        "description": "완성한 HTML 목업을 파일로 저장한다.",
        "parameters": {
            "type": "object",
            "properties": {
                "filename": {"type": "string", "description": "예: design.html"},
                "content": {"type": "string", "description": "완결된 HTML 전체"},
            },
            "required": ["filename", "content"],
        },
    },
}
class DesignerAgent(Agent):
    name = "디자이너"
    def __init__(self):
        self.client = OpenAI()

    def run(self, task: str) -> str:
        tools = [SAVE_DESIGN_TOOL]
        messages = [
            {"role": "system", "content": DESIGNER_SYSTEM},
            {"role": "user", "content": f"다음 요구사항으로 화면 목업을 만들어줘:\n\n{task}"},
        ]
        while True:
            response = self.client.chat.completions.create(
                model=MODEL, messages=messages, tools=tools,
            )
            msg = response.choices[0].message
            if not msg.tool_calls:
                if msg.content:
                    print(msg.content)
                break

            messages.append(msg)
            for call in msg.tool_calls:
                args = json.loads(call.function.arguments)
                print(f"  [{self.name}] 도구: {call.function.name} → {args.get('filename', '')}")
                if call.function.name == "save_design":
                    result = save_document(**args)
                else:
                    result = f"알 수 없는 도구: {call.function.name}"
                messages.append({
                    "role": "tool",
                    "tool_call_id": call.id,
                    "content": result,
                })

        return "output/design.html"
