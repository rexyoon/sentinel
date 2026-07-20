#ifndef SENTINEL_AGENT_MEMORY_COLLECTOR_H_
#define SENTINEL_AGENT_MEMORY_COLLECTOR_H_

#include <cstdint>

#include "metric_collector.h"

// /proc/meminfo 에서 읽은 메모리 정보 (단위: kB)
struct MemInfo {
  std::uint64_t total_kb = 0;      // 전체 메모리 (MemTotal)
  std::uint64_t available_kb = 0;  // 실제로 쓸 수 있는 메모리 (MemAvailable)
};

// 메모리 사용률을 측정하는 수집기. (gauge 방식, 상태 없음)
class MemoryCollector : public MetricCollector {
 public:
  const char* Name() const override { return "mem"; }
  double Sample() override;

 private:
  static MemInfo ReadMemInfo();
};

#endif  // SENTINEL_AGENT_MEMORY_COLLECTOR_H_