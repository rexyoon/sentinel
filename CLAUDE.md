# 파수꾼 (Sentinel) — AI 인프라 모니터링 시스템

## 프로젝트 개요
C++ 경량 에이전트가 서버 지표(/proc 기반)를 수집해 자체 TCP 프로토콜로
Kotlin(Ktor) 중앙 서버에 전송하고, LLM이 이상 징후를 한국어로 분석해
Discord로 알리는 모니터링 시스템. "나만의 AI 회사" 1호 직원 프로젝트.

## 저장소 구조 (모노레포)
- agent-cpp/      : C++17 수집 에이전트 (CMake)
- server-kotlin/  : Ktor 수집 서버 + REST/WebSocket API (Gradle)
- dashboard-web/  : React + TypeScript 대시보드 (Vite)
- docs/           : 기획서, 프로토콜 명세, ADR, 트러블슈팅 기록
- docker-compose.yml : PostgreSQL 16 + Redis 7 (로컬 개발용)

## 기술 스택 & 규칙
- C++17, CMake ≥3.20. 스마트 포인터/RAII 필수, 원시 new/delete 금지.
  외부 라이브러리 최소화(학습 목적) — 표준 라이브러리 우선.
- Kotlin 1.9+, Ktor 2.x, Exposed ORM, kotlinx.serialization, 코루틴 우선.
- PostgreSQL: metrics 테이블은 일 단위 RANGE 파티션. Redis: 최신값 캐시.
- 커밋 컨벤션: feat/fix/docs/refactor/chore + (모듈) 예: feat(agent): cpu collector

## 작업 방식 (중요)
1. 코드 변경 시 **파일 전체를 출력**한다. 부분 스니펫 금지.
2. 구현 전에 "무엇을/왜/어떻게" 3줄 계획을 먼저 보여주고 진행한다.
3. 이 프로젝트는 **학습이 목적**이다. 핵심 로직(CPU 계산, 소켓, 파티셔닝 등)에는
   "왜 이렇게 하는지" 주석과 함께, 작업 후 3줄 요약 설명을 덧붙인다.
4. 새 개념이 나오면 초심자에게 설명하듯 짧은 비유를 포함한다.
5. 내가 이해했는지 확인이 필요한 지점에서는 확인 질문을 1개 던진다.
6. 보안 기본값: 시크릿 하드코딩 금지(.env + .env.example), 입력 검증 필수.

## 테스트 & 빌드
- agent-cpp: `cmake -B build && cmake --build build && ./build/sentinel-agent`
- server-kotlin: `./gradlew run` / 테스트 `./gradlew test`
- 로컬 인프라: `docker compose up -d`

## 하지 말 것
- 요청하지 않은 기능 추가 (스코프 크리프 금지)
- 학습 목적을 건너뛰는 "마법 같은" 외부 라이브러리 도입
- main 브랜치 직접 커밋 (phase별 브랜치: phase1/agent-mvp 등)