// Sentinel Agent - Phase 2: 여러 지표를 1초마다 수집해 자체 TCP 프로토콜로 서버에 전송.
// 공통 인터페이스(MetricCollector) 덕에 지표 개수와 무관하게 루프 하나로 처리.
// 전송 형식(길이 접두 + JSON)은 docs/protocol.md 참고.

#include <unistd.h>  // gethostname

#include <chrono>
#include <csignal>
#include <cstdlib>  // std::getenv, std::atoi
#include <cstring>  // std::strncpy
#include <ctime>    // std::time
#include <iostream>
#include <memory>
#include <sstream>
#include <string>
#include <thread>
#include <vector>

#include "cpu_collector.h"
#include "memory_collector.h"
#include "metric_collector.h"
#include "tcp_sender.h"

namespace {

// Ctrl+C(SIGINT) 를 받으면 이 플래그를 0으로 바꿔 루프를 빠져나온다.
// volatile std::sig_atomic_t: 시그널 핸들러와 메인 루프가 '동시에' 건드려도
// 안전하게 읽고 쓸 수 있는 타입. (일반 bool 은 규격상 보장되지 않는다)
volatile std::sig_atomic_t g_running = 1;

void HandleSignal(int /*signum*/) { g_running = 0; }

// 이 머신의 호스트 이름을 얻는다 (JSON 의 "host" 필드로 쓴다).
std::string Hostname() {
  char buf[256];
  if (::gethostname(buf, sizeof(buf)) != 0) {
    return "unknown";
  }
  buf[sizeof(buf) - 1] = '\0';  // 잘렸을 경우 대비해 널 종단 보장
  return std::string(buf);
}

// 환경 변수를 읽되 없으면 기본값을 준다.
std::string EnvOr(const char* key, const std::string& fallback) {
  const char* v = std::getenv(key);
  return v ? std::string(v) : fallback;
}

}  // namespace

int main() {
  std::signal(SIGINT, HandleSignal);  // Ctrl+C 를 '깔끔한 종료'로

  // 전송 대상 서버. 기본값은 host.docker.internal — 컨테이너 안에서 '호스트 머신'을
  // 가리키는 Docker Desktop 전용 이름. (호스트에서 직접 실행하면 localhost 로 바꾼다)
  const std::string server_host = EnvOr("SENTINEL_SERVER_HOST", "host.docker.internal");
  const int server_port = std::atoi(EnvOr("SENTINEL_SERVER_PORT", "9400").c_str());
  const std::string host = Hostname();

  // 수집기들을 공통 인터페이스 포인터로 한 곳에 담는다 (RAII, new/delete 직접 안 씀).
  std::vector<std::unique_ptr<MetricCollector>> collectors;
  collectors.push_back(std::make_unique<CpuCollector>());
  collectors.push_back(std::make_unique<MemoryCollector>());

  TcpSender sender(server_host, server_port);

  std::cout << "sentinel-agent: host=" << host << " -> " << server_host << ":"
            << server_port << " (" << collectors.size() << " metrics, Ctrl+C to stop)\n";

  while (g_running) {
    std::this_thread::sleep_for(std::chrono::seconds(1));

    // 한 주기에 각 지표를 한 번만 Sample() 한다.
    // 같은 값으로 (a) JSON 본문과 (b) 화면 로그를 동시에 만든다.
    std::ostringstream metrics_json;  // [{"name":..,"value":..}, ...]
    std::ostringstream metrics_log;   // cpu=3.7% mem=30.2%
    for (std::size_t i = 0; i < collectors.size(); ++i) {
      const double value = collectors[i]->Sample();
      const char* name = collectors[i]->Name();
      if (i > 0) {
        metrics_json << ",";
      }
      metrics_json << "{\"name\":\"" << name << "\",\"value\":" << value << "}";
      metrics_log << name << "=" << value << "% ";
    }

    const std::time_t ts = std::time(nullptr);
    // JSON 을 손으로 조립한다. 스키마가 고정·단순하므로 외부 라이브러리 없이 충분.
    const std::string payload = "{\"host\":\"" + host +
                                "\",\"ts\":" + std::to_string(ts) +
                                ",\"metrics\":[" + metrics_json.str() + "]}";

    // 끊겨 있으면 재연결을 시도한 뒤 전송한다.
    if (!sender.connected()) {
      sender.Connect();
    }
    const bool ok = sender.Send(payload);

    std::cout << metrics_log.str() << (ok ? "-> sent" : "-> (offline)") << "\n";
  }

  std::cout << "sentinel-agent: stopped\n";
  return 0;
}
