# 파수꾼 (Sentinel)

AI 인프라 모니터링 시스템 — C++ 경량 에이전트가 서버 지표를 수집해 자체 TCP 프로토콜로
Kotlin(Ktor) 중앙 서버에 전송하고, LLM이 이상 징후를 한국어로 분석해 Discord로 알린다.

## 저장소 구조

| 디렉터리 | 설명 | 스택 |
|---|---|---|
| `agent-cpp/` | 지표 수집 에이전트 | C++17, CMake |
| `server-kotlin/` | 수집 서버 + REST/WebSocket API | Kotlin, Ktor 2.x |
| `dashboard-web/` | 웹 대시보드 | React, TypeScript, Vite |
| `docs/` | 기획서, 프로토콜 명세, ADR | — |

## 사전 준비

- Docker (PostgreSQL 16 + Redis 7 로컬 인프라)
- JDK 17+ (server-kotlin)
- CMake ≥3.20 + C++17 컴파일러 (agent-cpp)
- Node.js 18+ (dashboard-web)

```bash
# 최초 1회: 환경 변수 파일 생성
cp .env.example .env   # 값을 원하는 대로 수정
```

## 실행 방법

### 0. 로컬 인프라 (PostgreSQL + Redis)

```bash
docker compose up -d
docker compose ps        # 두 컨테이너가 healthy 인지 확인
```

### 1. agent-cpp

```bash
cd agent-cpp
cmake -B build
cmake --build build
./build/sentinel-agent   # → "hello sentinel"
```

### 2. server-kotlin

```bash
cd server-kotlin
./gradlew run            # Windows: gradlew.bat run
# 다른 터미널에서:
curl http://localhost:8080/health   # → {"status":"ok"}
```

> 기본 포트는 8080이며, 이미 사용 중이면 `SERVER_PORT` 환경 변수로 변경한다.
> 예: `SERVER_PORT=8081 ./gradlew run`

### 3. dashboard-web

```bash
cd dashboard-web
npm install
npm run dev              # → http://localhost:5173
```

## 개발 규칙

- 커밋 컨벤션: `feat/fix/docs/refactor/chore(모듈): 설명` — 예: `feat(agent): cpu collector`
- main 직접 커밋 금지, phase별 브랜치 사용 (예: `phase1/agent-mvp`)
- 시크릿은 `.env` 로만 관리 (`.env.example` 만 커밋)
