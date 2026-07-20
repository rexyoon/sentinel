#include "cpu_collector.h"

#include <fstream>
#include <sstream>
#include <string>

// 생성자 초기화 리스트로 prev_ 를 첫 스냅샷으로 채운다.
// (본문 {} 에서 대입하는 것보다 이쪽이 C++ 관용적)
CpuCollector::CpuCollector() : prev_(ReadCpuTimes()) {}

CpuTimes CpuCollector::ReadCpuTimes() {
  // ifstream 은 스코프를 벗어나면 파일을 자동으로 닫는다 (RAII).
  std::ifstream stat_file("/proc/stat");

  std::string line;
  std::getline(stat_file, line);  // 첫 줄만 필요 (전체 CPU 집계)

  std::istringstream iss(line);
  std::string label;
  iss >> label;  // 맨 앞 "cpu" 를 버린다

  CpuTimes times;
  std::uint64_t value = 0;
  int index = 0;
  // 필드 순서: user(0) nice(1) system(2) idle(3) iowait(4) irq(5) softirq(6)...
  while (iss >> value) {
    times.total += value;
    if (index == 3 || index == 4) {  // idle, iowait = '노는 시간'
      times.idle += value;
    }
    ++index;
  }
  return times;
}

double CpuCollector::Sample() {
  const CpuTimes now = ReadCpuTimes();

  const std::uint64_t total_delta = now.total - prev_.total;
  const std::uint64_t idle_delta = now.idle - prev_.idle;

  prev_ = now;  // 다음 호출을 위해 기준점을 갱신한다

  // 시간이 전혀 안 흘렀다면 0% 로 본다 (0 나누기 방어).
  if (total_delta == 0) {
    return 0.0;
  }
  return 100.0 * (1.0 - static_cast<double>(idle_delta) / total_delta);
}