// Sentinel Agent - Phase 1: CPU 사용률 수집기 (1단계, 단일 파일 버전).
// /proc/stat 첫 줄("cpu ...")은 부팅 후 CPU가 각 상태에서 보낸 '누적 시간'을
// jiffies(보통 1/100초) 단위로 준다. '지금 사용률'이 아니라 '누적'이므로,
// 두 시점 스냅샷의 차이(delta)로 사용률을 계산한다.
//
// 비유: 주행거리계(누적 km)로는 '지금 속도'를 못 구하지만,
//       1초 간격으로 두 번 읽어 차이를 내면 속도(초당 이동거리)가 나온다.

#include <chrono>
#include <cstdint>
#include <fstream>
#include <iostream>
#include <sstream>
#include <string>
#include <thread>

// /proc/stat 첫 줄에서 읽은 CPU 누적 시간.
struct CpuTimes {
  std::uint64_t idle = 0;   // 노는 시간 (idle + iowait)
  std::uint64_t total = 0;  // 모든 상태 시간의 합
};

// /proc/stat 의 첫 줄("cpu ...")을 읽어 누적 시간을 반환한다.
CpuTimes ReadCpuTimes() {
  // ifstream 은 스코프를 벗어나면 파일을 자동으로 닫는다 (RAII).
  // 원시 파일 핸들이나 명시적 close() 가 필요 없다.
  std::ifstream stat_file("/proc/stat");

  std::string line;
  std::getline(stat_file, line);  // 첫 줄만 필요 (전체 CPU 집계)

  // 줄을 토큰으로 쪼갠다: "cpu" 라벨 + 숫자들.
  std::istringstream iss(line);
  std::string label;
  iss >> label;  // 맨 앞 "cpu" 를 버린다

  CpuTimes times;
  std::uint64_t value = 0;
  int index = 0;
  // 필드 순서: user(0) nice(1) system(2) idle(3) iowait(4) irq(5) softirq(6)...
  while (iss >> value) {
    times.total += value;            // 모든 필드를 total 에 더한다
    if (index == 3 || index == 4) {  // idle, iowait = '노는 시간'
      times.idle += value;
    }
    ++index;
  }
  return times;
}

int main() {
  const CpuTimes t1 = ReadCpuTimes();                            // 1) 첫 스냅샷
  std::this_thread::sleep_for(std::chrono::seconds(1));          // 2) 1초 대기
  const CpuTimes t2 = ReadCpuTimes();                            // 3) 두 번째 스냅샷

  // 4) 두 스냅샷의 차이로 사용률 계산.
  const std::uint64_t total_delta = t2.total - t1.total;
  const std::uint64_t idle_delta = t2.idle - t1.idle;

  // 0으로 나누기 방어: 시간이 전혀 안 흘렀다면 계산 불가.
  if (total_delta == 0) {
    std::cerr << "no CPU time elapsed\n";
    return 1;
  }

  const double usage =
      100.0 * (1.0 - static_cast<double>(idle_delta) / total_delta);
  std::cout << "CPU usage: " << usage << " %\n";
  return 0;
}