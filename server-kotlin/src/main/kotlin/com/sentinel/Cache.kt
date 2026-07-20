package com.sentinel

import org.slf4j.LoggerFactory
import redis.clients.jedis.JedisPool

private val log = LoggerFactory.getLogger("Cache")

object Cache {
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
}