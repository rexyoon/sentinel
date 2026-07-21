# agents/openai_agent.py — OpenAI 호환(OpenAI/Kimi) 직원들의 공통 베이스.
# 루프는 여기 한 번만. 서브클래스는 이름·모델·프롬프트·저장경로만 채운다.

import json
import os

from openai import OpenAI

from agents.base import Agent
from tools import save_document

# OpenAI 형식 저장 도구
SAVE_TOOL = {
    "type": "function",
    "function": {
        "name": "save_document",
        "description": "완성한 문서/디자인을 파일로 저장한다.",
        "parameters": {
            "type": "object",
            "properties": {
                "filename": {"type": "string", "description": "저장할 파일 이름"},
                "content": {"type": "string", "description": "문서 전체 내용"},
            },
            "required": ["filename", "content"],
        },
    },
}


class OpenAICompatibleAgent(Agent):
    name = "직원"
    model = "gpt-4o"
    base_url = None            # None → OpenAI, 값 있으면 Kimi 등
    api_key_env = "OPENAI_API_KEY"
    system = "역할 지시문"
    output_path = "output/out.txt"

    def __init__(self):
        # base_url 만 바꾸면 OpenAI든 Kimi든 같은 SDK로 붙는다.
        self.client = OpenAI(base_url=self.base_url, api_key=os.getenv(self.api_key_env))

    def run(self, task: str) -> str:
        messages = [
            {"role": "system", "content": self.system},
            {"role": "user", "content": task},
        ]
        while True:
            response = self.client.chat.completions.create(
                model=self.model, messages=messages, tools=[SAVE_TOOL],
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
                result = save_document(**args)
                messages.append({
                    "role": "tool",
                    "tool_call_id": call.id,
                    "content": result,
                })

        return self.output_path