package com.sentinel

import io.ktor.network.selector.SelectorManager
import io.ktor.network.sockets.InetSocketAddress
import io.ktor.network.sockets.Socket
import io.ktor.network.sockets.aSocket
import io.ktor.network.sockets.openReadChannel
import io.ktor.utils.io.ByteReadChannel
import io.ktor.utils.io.readFully
import io.ktor.utils.io.readInt
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.serialization.Serializable
import kotlinx.serialization.json.Json
import org.slf4j.LoggerFactory

// ── 프레임 본문(JSON) 스키마. docs/protocol.md 와 1:1 대응 ──
// @Serializable 이 붙으면 컴파일러가 JSON ↔ 객체 변환 코드를 생성해준다.
@Serializable
data class Metric(val name: String, val value: Double)

@Serializable
data class MetricSnapshot(
    val host: String,
    val ts: Long,
    val metrics: List<Metric>,
)

private val log = LoggerFactory.getLogger("MetricsIngest")

// 알 수 없는 필드가 와도 무시(전방 호환). 스키마가 늘어도 옛 서버가 안 죽는다.
private val json = Json { ignoreUnknownKeys = true }

// 비정상적으로 큰 length 헤더로 인한 메모리 폭주를 막는 상한 (64 KiB).
private const val MAX_FRAME_BYTES = 64 * 1024

// 지표 수신 TCP 서버. 연결을 받아 각 연결을 독립 코루틴에서 처리한다.
suspend fun runMetricsIngestServer(port: Int, scope: CoroutineScope) {
    val selector = SelectorManager(Dispatchers.IO)
    val serverSocket = aSocket(selector).tcp().bind(InetSocketAddress("0.0.0.0", port))
    log.info("metrics ingest listening on :{} (length-prefixed JSON)", port)

    while (true) {
        val socket = serverSocket.accept()
        // 한 에이전트가 느려도 다른 연결을 막지 않도록 연결마다 코루틴을 띄운다.
        scope.launch { handleConnection(socket) }
    }
}

private suspend fun handleConnection(socket: Socket) {
    val remote = socket.remoteAddress
    log.info("agent connected: {}", remote)
    val input = socket.openReadChannel()
    try {
        // 프레임을 연속으로 읽는다: [4바이트 길이][그만큼의 JSON] 반복.
        while (true) {
            // readInt(): 정확히 4바이트를 big-endian 으로 읽는다 (연결이 닫히면 예외).
            val length = input.readInt()
            if (length <= 0 || length > MAX_FRAME_BYTES) {
                log.warn("invalid frame length {} from {}, closing", length, remote)
                break
            }
            // 정확히 length 바이트가 모일 때까지 읽는다 (TCP는 쪼개져 올 수 있으므로).
            val payload = ByteArray(length)
            input.readFully(payload)

            val snapshot = json.decodeFromString<MetricSnapshot>(payload.decodeToString())

            // 저장(과거 이력) + 캐시(최신값). 블로킹 호출이지만 여기는 IO 디스패처.
            Persistence.save(snapshot)
            Cache.setLatest(snapshot)

            val summary = snapshot.metrics.joinToString("  ") { "${it.name}=${it.value}%" }
            log.info("[{}] ts={} {} (stored)", snapshot.host, snapshot.ts, summary)
        }
    } catch (e: Exception) {
        // EOF(에이전트가 연결 종료)도 예외로 온다 — 정상적인 흐름으로 취급.
        log.info("agent disconnected: {} ({})", remote, e.javaClass.simpleName)
    } finally {
        socket.close()
    }
}
