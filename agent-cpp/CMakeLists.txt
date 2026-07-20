# 왜 3.20인가: FetchContent, presets 등 이후 단계에서 쓸 기능이 안정화된 버전이자
# 대부분의 배포판(Ubuntu 22.04+)에 기본 탑재된 하한선이다.
cmake_minimum_required(VERSION 3.20)

project(sentinel_agent
        VERSION 0.1.0
        DESCRIPTION "Sentinel lightweight metrics collection agent"
        LANGUAGES CXX)

# 왜 표준을 '요구'하는가: REQUIRED가 없으면 컴파일러가 C++17을 지원하지 않아도
# 조용히 낮은 표준으로 빌드된다. 실패는 시끄럽게, 일찍 나는 것이 좋다.
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)  # -std=gnu++17 이 아닌 순수 -std=c++17 사용

add_executable(sentinel-agent src/main.cpp)

# 경고를 에러 수준으로 올려서 습관을 잡는다 (학습 목적).
if(MSVC)
  target_compile_options(sentinel-agent PRIVATE /W4)
else()
  target_compile_options(sentinel-agent PRIVATE -Wall -Wextra -Wpedantic)
endif()
