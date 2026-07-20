#ifndef SENTINEL_AGENT_CPU_COLLECTOR_H_
#define SENTINEL_AGENT_CPU_COLLECTOR_H_

#include <cstdint>

#include "metric_collector.h"

// /proc/stat 첫 줄에서 읽은 CPU 누적 시간.
struct CpuTimes {
  std::uint64_t idle = 0;   // 노는 시간 (idle + iowait)
  std::uint64_t total = 0;  // 모든 상태 시간의 합
};

// CPU 사용률을 '연속으로' 측정하는 수집기. (counter 방식)
class CpuCollector : public MetricCollector {
 public:
  CpuCollector();

  // override: "이건 부모의 가상 함수를 재정의한 것"이라고 컴파일러에 명시.
  // 실수로 시그니처가 어긋나면(예: const 빠뜨림) 컴파일 에러로 잡아준다.
  const char* Name() const override { return "cpu"; }
  double Sample() override;

 private:
  static CpuTimes ReadCpuTimes();
  CpuTimes prev_;
};

#endif  // SENTINEL_AGENT_CPU_COLLECTOR_H_