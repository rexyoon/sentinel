# pm_agent.py — 기획자(PM) 에이전트: 의뢰 → 요구사항 정의서 작성 → 저장.
# 에이전트의 심장인 '수동 루프'를 직접 구현한다.

from tools import save_document, SAVE_DOCUMENT_TOOL

MODEL = "claude-opus-4-8"

# 역할 지시문(system prompt): 이 에이전트가 '누구'이고 '무엇을' 하는지.
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


def run_pm(client, request: str) -> None:
    tools = [SAVE_DOCUMENT_TOOL]
    # 대화 기록. API는 상태가 없어서 매번 전체 대화를 다시 보낸다.
    messages = [{"role": "user", "content": request}]

    # ── 에이전트 루프: Claude가 도구를 그만 부를 때까지 돈다 ──
    while True:
        response = client.messages.create(
            model=MODEL,
            max_tokens=8000,
            system=PM_SYSTEM,
            tools=tools,
            messages=messages,
        )

        # stop_reason 이 'tool_use'가 아니면(=end_turn) 작업 끝.
        if response.stop_reason != "tool_use":
            for block in response.content:
                if block.type == "text":
                    print(block.text)
            break

        # 1) 방금 받은 assistant 응답(도구 호출 포함)을 대화에 추가한다.
        messages.append({"role": "assistant", "content": response.content})

        # 2) 요청된 도구를 실제로 실행하고, 결과를 모은다.
        tool_results = []
        for block in response.content:
            if block.type == "tool_use":
                print(f"  [도구 호출] {block.name} → {block.input.get('filename', '')}")
                if block.name == "save_document":
                    result = save_document(**block.input)
                else:
                    result = f"알 수 없는 도구: {block.name}"
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,   # 어느 호출에 대한 결과인지 짝을 맞춘다
                    "content": result,
                })

        # 3) 도구 결과를 user 메시지로 되돌려주고, 루프를 다시 돈다.
        messages.append({"role": "user", "content": tool_results})