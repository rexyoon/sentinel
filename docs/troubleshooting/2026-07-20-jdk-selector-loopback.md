# JDK `Selector.open()` 실패 — "Unable to establish loopback connection"

- 날짜: 2026-07-20
- 환경: Windows 11 IoT Enterprise LTSC 2024, Oracle JDK 17.0.12
- 증상: `./gradlew` 실행 시 즉시 실패
  ```
  java.io.IOException: Unable to establish loopback connection
  Caused by: java.net.SocketException: Invalid argument: connect
      at sun.nio.ch.UnixDomainSockets.connect0(Native Method)
  ```

## 원인 분석 과정

1. Gradle 데몬 문제로 의심 → `--no-daemon`, IPv4 강제 모두 실패.
2. 최소 재현 코드(`Selector.open()` 한 줄)를 순수 `java`로 실행 → **동일 실패**.
   즉 Gradle이 아니라 이 머신의 JVM 레벨 문제.
3. 스택트레이스 분석: JDK 16+는 Windows에서 NIO 파이프(Selector의 wakeup 채널)를
   **유닉스 도메인 소켓(AF_UNIX)** 으로 만든다. 이때 소켓 파일을 임시 폴더에 생성하는데,
   그 `connect()`가 EINVAL로 실패.
4. `afunix` 커널 드라이버는 정상 실행 중. 소켓 파일 위치를 바꿔가며 실험:

   | 소켓 파일 위치 | 결과 |
   |---|---|
   | `C:\Users\<user>\AppData\Local\Temp` (기본값) | ❌ 실패 |
   | `C:\Users\Public` | ✅ 성공 |
   | `C:\Users\<user>\.uds-tmp` | ✅ 성공 |

   → **Temp 폴더에서만 실패.** 백신/EDR이 Temp 폴더의 소켓 파일 생성·연결을
   차단하는 것으로 추정 (Temp는 악성코드 활동 감시 1순위 폴더라 보안 제품이 가장 공격적으로 개입한다).

## 해결

JDK가 유닉스 도메인 소켓 파일을 만들 위치를 Temp 밖으로 지정한다:

```
-Djdk.net.unixdomain.tmpdir=C:\Users\<user>\.uds-tmp
```

모든 JVM(Gradle 런처·데몬·앱)에 일괄 적용하려면 사용자 환경 변수로 등록:

```powershell
mkdir $HOME\.uds-tmp
setx JAVA_TOOL_OPTIONS "-Djdk.net.unixdomain.tmpdir=C:\Users\<user>\.uds-tmp"
```

부작용: 모든 `java` 실행 시 `Picked up JAVA_TOOL_OPTIONS: ...` 한 줄이 stderr에 출력됨 (무해).

## 배운 것

- "Gradle이 안 된다" ≠ Gradle 문제. **최소 재현 코드로 레이어를 벗겨가며** 범위를 좁힐 것.
- Java NIO의 `Selector`는 자기 자신을 깨우기 위한 내부 통신 채널(파이프)이 필요하고,
  Windows JDK 16+는 이를 AF_UNIX 소켓으로 구현한다. 비유: 초인종(wakeup 채널)이
  고장난 집은 문(서버 소켓)이 멀쩡해도 손님을 못 받는다.
- 보안 제품은 Temp 폴더에 유난히 민감하다. "Temp에서만 안 되는" 증상이면 AV를 의심할 것.
