package com.sentinel

import io.ktor.http.ContentType
import io.ktor.server.application.Application
import io.ktor.server.application.call
import io.ktor.server.engine.embeddedServer
import io.ktor.server.netty.Netty
import io.ktor.server.response.respondText
import io.ktor.server.routing.get
import io.ktor.server.routing.routing

// Phase 0: 서버가 "살아있음"만 알리는 최소 구성.
// embeddedServer = 서버를 코드 안에서 직접 띄우는 방식 (별도 톰캣 같은 컨테이너 불필요).
// 비유하자면, 건물(WAS)에 입주하는 대신 캠핑카(Netty)를 몰고 다니는 것.
fun main() {
    // 포트를 코드에 못 박지 않고 환경 변수로 뺀다 (12-factor 원칙).
    // 같은 머신에서 다른 서비스가 8080을 쓰고 있어도 코드 수정 없이 피할 수 있다.
    val port = System.getenv("SERVER_PORT")?.toIntOrNull() ?: 8080
    embeddedServer(Netty, port = port, host = "0.0.0.0", module = Application::module)
        .start(wait = true) // wait=true: 메인 스레드를 잡아둬서 프로세스가 바로 종료되지 않게 함
}

fun Application.module() {
    routing {
        get("/health") {
            // Phase 0에서는 직렬화 라이브러리 없이 JSON 문자열을 직접 반환한다.
            // kotlinx.serialization은 실제 DTO가 생기는 Phase 2에서 도입 예정.
            call.respondText("""{"status":"ok"}""", ContentType.Application.Json)
        }
    }
}
