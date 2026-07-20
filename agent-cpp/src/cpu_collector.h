#ifndef SENTINEL_AGENT_CPU_COLLECTOR_H_
#define SENTINEL_AGENT_CPU_COLLECTOR_H_

#include <cstdint>

// /proc/stat 첫 줄에서 읽은 cpu 누적 시간
struct CpuTimes{
    std::uint64_t idle = 0;
    std::uint64_t total = 0;
};
// CPU 사용률을 '연속으로' 측정하는 수집기.
// 이전 스냅샷을 내부에 기억했다가, Sample() 을 부를 때마다
// 직전 호출 이후의 사용률(%)을 계산해 돌려준다.
class CpuCollector{
    public:
    CpuCollector();
    double Sample();
    private:
        static CpuTimes ReadCpuTimes();
        CpuTimes prev_;
};
#endif //SENTINEL_AGENT_CPU_COLLECTOR_H_
