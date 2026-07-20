# AI 회사 (작은 SI 팀)

역할을 맡은 AI 에이전트들이 협업해, 고객의 프로젝트 의뢰 한 줄을
소프트웨어 산출물(요구사항 정의 → 코드)로 만들어내는 멀티 에이전트 시스템.

```
고객 의뢰  ──▶  기획자(PM)  ──▶  개발자  ──▶  산출물
"할 일 앱"      요구사항 정의     코드        (문서 + 코드)
```

## 사전 준비
- Python 3.11+
- (마지막 단계) Anthropic API 키 → `.env` 에 `ANTHROPIC_API_KEY`

## 설치
```bash
python -m venv .venv
.venv\Scripts\activate      # Windows PowerShell: .venv\Scripts\Activate.ps1
pip install -r requirements.txt
cp .env.example .env         # 키는 나중에 채움
```

## 로드맵
1. 기획자(PM) 에이전트 — 의뢰 → 요구사항 정의
2. 개발자 에이전트 + 인수인계
3. 오케스트레이터(매니저)
4. API 키 연결 후 실제 구동
