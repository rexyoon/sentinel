#!/usr/bin/env bash
# agent-cpp 를 리눅스 컨테이너 안에서 빌드하고 실행한다.
# /proc 기반 수집기는 리눅스에서만 동작하므로, Windows 호스트에서도
# 컨테이너를 '리눅스 실행 환경'으로 빌려 쓴다.
set -euo pipefail   # 에러가 나면 즉시 멈추고(-e), 미정의 변수 사용 금지(-u)

IMAGE=sentinel-agent-dev
cd "$(dirname "${BASH_SOURCE[0]}")"   # 스크립트가 있는 agent-cpp 로 이동

# Docker Desktop(Windows)에는 윈도우식 경로를 넘겨야 한다.
# pwd -W 는 Git Bash에서 'C:/Users/...' 형태의 윈도우 경로를 준다.
HERE_WIN="$(pwd -W)"

# MSYS가 컨테이너 내부 경로(/work)를 윈도우 경로로 바꿔치기하는 것을 막는다.
# 호스트 경로(HERE_WIN)는 이미 윈도우식이라 변환이 필요 없다.
export MSYS_NO_PATHCONV=1

# 1) 툴체인 이미지가 없으면 빌드 (최초 1회, 이후엔 캐시라서 즉시 끝남)
docker build -t "$IMAGE" -f "$HERE_WIN/Dockerfile.dev" "$HERE_WIN"

# 2) 소스를 컨테이너에 마운트(-v)해 그 안에서 빌드+실행
#    build-linux/ 를 Windows용 build/ 와 분리하는 이유:
#    컴파일 결과물(오브젝트 파일)은 OS마다 형식이 달라서, 두 OS 것이
#    한 폴더에 섞이면 링크가 깨진다.
docker run --rm -v "$HERE_WIN:/work" -w /work "$IMAGE" bash -c "\
    cmake -B build-linux -G Ninja && \
    cmake --build build-linux && \
    ./build-linux/sentinel-agent"
