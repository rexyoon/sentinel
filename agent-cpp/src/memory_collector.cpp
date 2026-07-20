#include "memory_collector.h"

#include <fstream>
#include <sstream>
#include <string>

MemInfo MemoryCollector::ReadMemInfo() {
  // ifstream 은 스코프를 벗어나면 자동으로 닫힌다 (RAII).
  std::ifstream meminfo_file("/proc/meminfo");

  std::string line;
  MemInfo info;
  // /proc/stat 과 달리 여러 줄이므로, 줄마다 훑으며 원하는 키만 집는다.
  while (std::getline(meminfo_file, line)) {
    std::istringstream iss(line);
    std::string key;
    std::uint64_t value = 0;
    iss >> key >> value;  // 예: "MemTotal:" 16289980  (뒤의 "kB" 는 안 읽음)

    if (key == "MemTotal:") {
      info.total_kb = value;
    } else if (key == "MemAvailable:") {
      info.available_kb = value;
    }
  }
  return info;
}

double MemoryCollector::Sample() {
  const MemInfo info = ReadMemInfo();

  // 못 읽었으면(총량 0) 0% 로 방어한다.
  if (info.total_kb == 0) {
    return 0.0;
  }

  const std::uint64_t used_kb = info.total_kb - info.available_kb;
  return 100.0 * static_cast<double>(used_kb) / info.total_kb;
}