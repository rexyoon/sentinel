package com.sentinel

import io.ktor.http.ContentType
import io.ktor.server.application.Application
import io.ktor.server.application.call
import io.ktor.server.engine.embeddedServer
import io.ktor.server.netty.Netty
import io.ktor.server.response.respondText
import io.ktor.server.routing.get
import io.ktor.server.routing.routing
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch

// 서버는 두 귀로 듣는다:
//  - HTTP(Netty)  : /health 등 REST — SERVER_PORT (기본 8080)
//  - TCP(ktor-network): 자체 프로토콜로 오는 지표 — INGEST_PORT (기본 9400)
// embeddedServer = 서버를 코드 안에서 직접 띄우는 방식 (별도 톰캣 같은 컨테이너 불필요).
fun main() {
    // 포트를 코드에 못 박지 않고 환경 변수로 뺀다 (12-factor 원칙).
    val httpPort = System.getenv("SERVER_PORT")?.toIntOrNull() ?: 8080
    val ingestPort = System.getenv("INGEST_PORT")?.toIntOrNull() ?: 9400

    // 지표 수신 TCP 서버를 백그라운드 코루틴으로 띄운다.
    // (아래 HTTP 서버가 wait=true 로 메인 스레드를 잡으므로, TCP는 별도로 돌려야 한다.)
    val scope = CoroutineScope(Dispatchers.IO)
    scope.launch { runMetricsIngestServer(ingestPort, scope) }

    embeddedServer(Netty, port = httpPort, host = "0.0.0.0", module = Application::module)
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
