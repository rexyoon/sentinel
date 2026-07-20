package com.sentinel

import org.slf4j.LoggerFactory
import redis.clients.jedis.JedisPool
import kotlinx.serialization.Serializable
private val log = LoggerFactory.getLogger("Cache")

object Cache {
    @Serializable
    data class LatestEntry(val host: String, val name: String, val value: Double)
    private lateinit var pool: JedisPool
    fun init(host: String, port: Int) {
        pool = JedisPool(host, port)
        log.info("redis connected: {}:{}", host, port)
    }
    fun setLatest(snapshot: MetricSnapshot) {
        pool.resource.use { jedis ->
            for (metric in snapshot.metrics) {
                jedis.set("latest:${snapshot.host}:${metric.name}", metric.value.toString())
            }
        }
    }

    // Redis에 저장된 모든 최신값을 읽어 목록으로 돌려준다.
    fun getAllLatest(): List<LatestEntry> {
        pool.resource.use { jedis ->
            // latest:{host}:{name} 패턴의 키를 전부 찾는다 (학습 규모라 keys 로 충분).
            val keys = jedis.keys("latest:*")
            return keys.mapNotNull { key ->
                val parts = key.split(":")          // ["latest", host, name]
                if (parts.size != 3) return@mapNotNull null
                val value = jedis.get(key)?.toDoubleOrNull() ?: return@mapNotNull null
                LatestEntry(parts[1], parts[2], value)
            }
        }
    }
}