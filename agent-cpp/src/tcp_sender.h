#ifndef SENTINEL_AGENT_TCP_SENDER_H_
#define SENTINEL_AGENT_TCP_SENDER_H_

#include <string>

// 자체 프로토콜(길이 접두 + JSON)로 지표 프레임을 서버에 보내는 TCP 송신기.
// 소켓 파일 디스크립터(fd)라는 OS 자원을 들고 있으므로 RAII로 정리한다.
//
// 비유: fd 는 도서관에서 빌린 열쇠다. 다 쓰면 반드시 반납(close)해야 하고,
//       열쇠 하나를 두 사람이 나눠 가지면(복사) 반납이 꼬인다 → 복사 금지.
class TcpSender {
 public:
  TcpSender(std::string host, int port);
  ~TcpSender();

  // 복사 금지: fd 를 두 객체가 공유하면 이중 close(반납 두 번)가 난다.
  TcpSender(const TcpSender&) = delete;
  TcpSender& operator=(const TcpSender&) = delete;

  // 서버에 연결한다. 성공하면 true. (이미 연결돼 있으면 즉시 true)
  bool Connect();

  // payload 를 [4바이트 길이][payload] 프레임으로 보낸다. 성공하면 true.
  // 전송 중 연결이 끊기면 내부 fd 를 닫고 false 를 반환한다(호출 측이 재연결 결정).
  bool Send(const std::string& payload);

  bool connected() const { return fd_ >= 0; }

 private:
  void Close();

  std::string host_;
  int port_;
  int fd_ = -1;  // -1 = 연결 안 됨
};

#endif  // SENTINEL_AGENT_TCP_SENDER_H_
