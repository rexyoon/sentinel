package com.sentinel

import io.ktor.http.ContentType
import io.ktor.http.HttpHeaders
import io.ktor.serialization.kotlinx.json.json
import io.ktor.server.application.Application
import io.ktor.server.application.call
import io.ktor.server.application.install
import io.ktor.server.engine.embeddedServer
import io.ktor.server.netty.Netty
import io.ktor.server.plugins.contentnegotiation.ContentNegotiation
import io.ktor.server.plugins.cors.routing.CORS
import io.ktor.server.response.respond
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

    // 저장소 초기화. 기본값은 이 머신의 호스트 포트(.env: 5433/6380)에 맞춘다.
    Persistence.init(
        jdbcUrl = System.getenv("DB_URL") ?: "jdbc:postgresql://localhost:5433/sentinel",
        user = System.getenv("DB_USER") ?: "sentinel",
        password = System.getenv("DB_PASSWORD") ?: "sentinel-dev-2026",
    )
    Cache.init(
        host = System.getenv("REDIS_HOST") ?: "localhost",
        port = System.getenv("REDIS_PORT")?.toIntOrNull() ?: 6380,
    )

    // 지표 수신 TCP 서버를 백그라운드 코루틴으로 띄운다.
    // (아래 HTTP 서버가 wait=true 로 메인 스레드를 잡으므로, TCP는 별도로 돌려야 한다.)
    val scope = CoroutineScope(Dispatchers.IO)
    scope.launch { runMetricsIngestServer(ingestPort, scope) }

    embeddedServer(Netty, port = httpPort, host = "0.0.0.0", module = Application::module)
        .start(wait = true) // wait=true: 메인 스레드를 잡아둬서 프로세스가 바로 종료되지 않게 함
}

fun Application.module() {
    // 응답 객체(LatestEntry 등)를 JSON으로 자동 직렬화한다.
    install(ContentNegotiation) { json() }

    // 대시보드는 5173, 이 서버는 8082 — 출처가 달라서(cross-origin) 브라우저가 막는다.
    // CORS로 "다른 출처의 호출을 허용"한다. (학습용이라 anyHost, 운영이면 좁혀야 함)
    install(CORS) {
        anyHost()
        allowHeader(HttpHeaders.ContentType)
    }

    routing {
        get("/health") {
            call.respondText("""{"status":"ok"}""", ContentType.Application.Json)
        }

        // 모든 지표의 최신값 (Redis에서). call.respond 가 객체를 JSON으로 바꿔 보낸다.
        get("/api/latest") {
            call.respond(Cache.getAllLatest())
        }
    }
}
