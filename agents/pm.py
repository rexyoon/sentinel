# agents/pm.py — 기획자(PM): 의뢰 → 요구사항 정의서. 두뇌=Claude.

import anthropic

from agents.base import Agent
from tools import save_document, SAVE_DOCUMENT_TOOL

MODEL = "claude-opus-4-8"

PM_SYSTEM = """너는 작은 SI 회사의 기획자(PM)다.
고객의 프로젝트 의뢰 한 줄을 받아, 개발자가 바로 착수할 수 있는
'요구사항 정의서'를 한국어 마크다운으로 작성한다.

반드시 포함할 것:
- 프로젝트 개요 (한 문단)
- 핵심 기능 목록
- 화면 목록
- 데이터 항목(엔티티)
- 제약사항 / 가정

문서를 완성하면 save_document 도구로 requirements.md 파일에 저장하라."""


class PMAgent(Agent):
    name = "기획자"

    def __init__(self):
        self.client = anthropic.Anthropic()  # 자기 두뇌를 스스로 소유

    def run(self, task: str) -> str:
        tools = [SAVE_DOCUMENT_TOOL]
        messages = [{"role": "user", "content": task}]

        while True:
            response = self.client.messages.create(
                model=MODEL, max_tokens=8000,
                system=PM_SYSTEM, tools=tools, messages=messages,
            )
            if response.stop_reason != "tool_use":
                for block in response.content:
                    if block.type == "text":
                        print(block.text)
                break

            messages.append({"role": "assistant", "content": response.content})
            tool_results = []
            for block in response.content:
                if block.type == "tool_use":
                    print(f"  [{self.name}] 도구: {block.name} → {block.input.get('filename', '')}")
                    if block.name == "save_document":
                        result = save_document(**block.input)
                    else:
                        result = f"알 수 없는 도구: {block.name}"
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": result,
                    })
            messages.append({"role": "user", "content": tool_results})

        return "output/requirements.md"  # 산출물 경로 반환 → 다음 직원이 이어받음