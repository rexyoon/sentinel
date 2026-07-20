#include "tcp_sender.h"

#include <arpa/inet.h>   // htonl
#include <netdb.h>       // getaddrinfo, freeaddrinfo
#include <sys/socket.h>  // socket, connect, send
#include <unistd.h>      // close

#include <cstdint>
#include <string>
#include <utility>  // std::move

TcpSender::TcpSender(std::string host, int port)
    : host_(std::move(host)), port_(port) {}

TcpSender::~TcpSender() { Close(); }

void TcpSender::Close() {
  if (fd_ >= 0) {
    ::close(fd_);  // 앞의 :: 는 '전역(OS) 함수'라는 표시. 우리 멤버 Close 와 헷갈리지 않게.
    fd_ = -1;
  }
}

bool TcpSender::Connect() {
  if (fd_ >= 0) {
    return true;  // 이미 연결돼 있음
  }

  // getaddrinfo: 호스트 이름("host.docker.internal" 같은)을 실제 주소로 변환한다.
  // IP 문자열이든 도메인이든 동일하게 처리해준다.
  addrinfo hints{};                 // {} 로 전 필드 0 초기화
  hints.ai_family = AF_INET;        // IPv4
  hints.ai_socktype = SOCK_STREAM;  // TCP

  addrinfo* result = nullptr;
  const std::string port_str = std::to_string(port_);
  if (::getaddrinfo(host_.c_str(), port_str.c_str(), &hints, &result) != 0) {
    return false;  // 이름 해석 실패
  }

  // 후보 주소들을 순회하며 처음으로 연결되는 것을 쓴다.
  int fd = -1;
  for (addrinfo* rp = result; rp != nullptr; rp = rp->ai_next) {
    fd = ::socket(rp->ai_family, rp->ai_socktype, rp->ai_protocol);
    if (fd < 0) {
      continue;
    }
    if (::connect(fd, rp->ai_addr, rp->ai_addrlen) == 0) {
      break;  // 연결 성공
    }
    ::close(fd);  // 이 주소는 실패 → 닫고 다음 후보로
    fd = -1;
  }
  ::freeaddrinfo(result);  // getaddrinfo 가 할당한 메모리 반납

  fd_ = fd;
  return fd_ >= 0;
}

bool TcpSender::Send(const std::string& payload) {
  if (fd_ < 0) {
    return false;
  }

  // 4바이트 길이 헤더를 네트워크 바이트 순서(big-endian)로 만든다.
  // htonl = Host TO Network Long. 내 CPU 엔디안과 무관하게 항상 big-endian 바이트를 준다.
  const std::uint32_t be_length = htonl(static_cast<std::uint32_t>(payload.size()));

  // [헤더 4바이트][본문] 을 한 버퍼로 합쳐 한 번에 보낸다.
  std::string frame;
  frame.reserve(sizeof(be_length) + payload.size());
  frame.append(reinterpret_cast<const char*>(&be_length), sizeof(be_length));
  frame.append(payload);

  // send 는 요청한 만큼을 '한 번에 다' 보낸다는 보장이 없다(부분 전송).
  // 그래서 전부 나갈 때까지 반복한다.
  std::size_t sent = 0;
  while (sent < frame.size()) {
    // MSG_NOSIGNAL: 상대가 끊긴 소켓에 쓰면 SIGPIPE 로 프로세스가 죽는데, 그걸 막고
    //               대신 에러(-1)를 돌려받는다.
    const ssize_t n =
        ::send(fd_, frame.data() + sent, frame.size() - sent, MSG_NOSIGNAL);
    if (n <= 0) {
      Close();  // 연결이 끊겼다 → 닫아서 다음 주기에 재연결하도록
      return false;
    }
    sent += static_cast<std::size_t>(n);
  }
  return true;
}
