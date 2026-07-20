// Sentinel Agent - Phase 1: CPU 사용률을 1초마다 계속 수집해 출력한다.
// TCP 전송은 Phase 2에서 붙인다. 지금은 stdout 으로만 내보낸다.

#include <chrono>
#include <csignal>
#include <iostream>
#include <thread>

#include "cpu_collector.h"

namespace {

// Ctrl+C(SIGINT) 를 받으면 이 플래그를 0으로 바꿔 루프를 빠져나온다.
// volatile std::sig_atomic_t: 시그널 핸들러와 메인 루프가 '동시에' 건드려도
// 안전하게 읽고 쓸 수 있는 타입. (일반 bool 은 규격상 안전이 보장되지 않는다)
volatile std::sig_atomic_t g_running = 1;

void HandleSignal(int /*signum*/) { g_running = 0; }

}  // namespace

int main() {
  // Ctrl+C 를 강제 종료가 아니라 '깔끔한 종료'로 바꾼다.
  std::signal(SIGINT, HandleSignal);

  CpuCollector collector;  // 생성 시 기준 스냅샷을 찍는다

  std::cout << "sentinel-agent: collecting CPU usage (Ctrl+C to stop)\n";

  while (g_running) {
    std::this_thread::sleep_for(std::chrono::seconds(1));
    const double usage = collector.Sample();
    std::cout << "CPU usage: " << usage << " %\n";
  }

  std::cout << "sentinel-agent: stopped\n";
  return 0;
}