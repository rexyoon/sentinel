# agent-cpp 를 리눅스 컨테이너 안에서 빌드하고 실행한다 (PowerShell 판).
# dev.sh 와 동일한 일을 하되, PowerShell 에서 바로 실행할 수 있다.
#   PS> .\dev.ps1
# /proc 기반 수집기는 리눅스에서만 동작하므로 컨테이너를 리눅스 실행 환경으로 쓴다.
$ErrorActionPreference = "Stop"   # 명령이 실패하면 즉시 멈춘다

$Image = "sentinel-agent-dev"
$Here = $PSScriptRoot             # 이 스크립트가 있는 agent-cpp 폴더

# 1) 툴체인 이미지가 없으면 빌드 (최초 1회, 이후엔 캐시)
docker build -t $Image -f "$Here\Dockerfile.dev" $Here

# 2) 소스를 마운트해 컨테이너 안에서 빌드+실행.
#    build-linux/ 는 Windows용 build/ 와 분리한다 (OS별 오브젝트 파일 혼용 방지).
#    -e ...: 컨테이너 속 에이전트가 호스트에서 도는 서버(9400)로 지표를 보내도록 지정.
#    host.docker.internal = 컨테이너에서 '호스트 머신'을 가리키는 이름. 서버가 안 떠 있으면
#    에이전트는 "-> (offline)" 로 표시하며 계속 돈다(치명적 아님).
docker run --rm `
    -e SENTINEL_SERVER_HOST=host.docker.internal `
    -e SENTINEL_SERVER_PORT=9400 `
    -v "${Here}:/work" -w /work $Image `
    bash -c "cmake -B build-linux -G Ninja && cmake --build build-linux && ./build-linux/sentinel-agent"
