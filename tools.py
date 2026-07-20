# tools.py — 에이전트가 쓸 수 있는 '손'(도구)들.
# 도구 = (1) 실제 실행되는 파이썬 함수 + (2) LLM에게 알려줄 명세(스키마)

import os

# 산출물을 저장할 폴더 (gitignore에 등록해 둠).
OUTPUT_DIR = "output"


def save_document(filename: str, content: str) -> str:
    """문서(요구사항 정의서 등)를 output/ 폴더에 파일로 저장한다."""
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    # 경로 탈출(../etc/passwd 같은) 방지: 파일 '이름'만 취한다.
    safe_name = os.path.basename(filename)
    path = os.path.join(OUTPUT_DIR, safe_name)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    return f"저장 완료: {path} ({len(content)}자)"


# LLM에게 넘길 도구 명세(JSON 스키마).
# Claude는 name/description을 보고 이 도구를 언제 부를지 판단한다.
SAVE_DOCUMENT_TOOL = {
    "name": "save_document",
    "description": (
        "완성한 문서(요구사항 정의서 등)를 파일로 저장한다. "
        "문서를 다 작성했으면 반드시 이 도구로 저장하라."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "filename": {
                "type": "string",
                "description": "저장할 파일 이름 (예: requirements.md)",
            },
            "content": {
                "type": "string",
                "description": "문서의 전체 내용 (마크다운)",
            },
        },
        "required": ["filename", "content"],
    },
}