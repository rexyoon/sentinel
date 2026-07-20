// Sentinel Agent - Phase 0: 빌드 파이프라인 검증용 엔트리 포인트.
// 이후 단계에서 /proc 기반 수집기(collector)와 TCP 전송기(sender)가 여기에 연결된다.
#include <iostream>

int main() {
  std::cout << "hello sentinel\n";
  return 0;
}
