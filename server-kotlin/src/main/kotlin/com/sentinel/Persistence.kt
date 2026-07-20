package com.sentinel

import com.zaxxer.hikari.HikariConfig
import com.zaxxer.hikari.HikariDataSource
import org.jetbrains.exposed.sql.Database
import org.jetbrains.exposed.sql.Table
import org.jetbrains.exposed.sql.insert
import org.jetbrains.exposed.sql.javatime.timestamp
import org.jetbrains.exposed.sql.transactions.transaction
import org.slf4j.LoggerFactory
import java.time.Instant
import java.time.LocalDate
import java.time.ZoneOffset

private val log = LoggerFactory.getLogger("Persistence")

// metrics '부모' 테이블 매핑. 실제 저장은 날짜별 자식 파티션으로 자동 라우팅된다.
// 파티션 테이블이라 대리 키(PK)를 두지 않는다 (docs/schema.sql 참고).
object MetricsTable : Table("metrics") {
    val ts = timestamp("ts")
    val host = text("host")
    val name = text("name")
    val value = double("value")
}

// 지표를 PostgreSQL 파티션 테이블에 적재한다.
object Persistence {
    private lateinit var dataSource: HikariDataSource

    // 이미 만든 파티션은 다시 만들지 않도록 기억한다 (매 저장마다 DDL 날리면 낭비).
    private val ensuredDates = HashSet<LocalDate>()

    fun init(jdbcUrl: String, user: String, password: String) {
        val config = HikariConfig().apply {
            this.jdbcUrl = jdbcUrl
            username = user
            this.password = password
            maximumPoolSize = 4              // 학습용이라 작게
            driverClassName = "org.postgresql.Driver"
        }
        dataSource = HikariDataSource(config)
        // Exposed 를 이 커넥션 풀 위에 연결한다.
        Database.connect(dataSource)
        log.info("postgres connected: {}", jdbcUrl)
    }

    // 해당 날짜의 파티션이 없으면 만든다. (하루에 한 번만 실제 DDL 실행)
    private fun ensurePartition(date: LocalDate) {
        if (date in ensuredDates) return

        // 이름/경계는 날짜에서만 유도된다(사용자 입력 아님) → SQL 조립해도 안전.
        val table = "metrics_%04d_%02d_%02d".format(date.year, date.monthValue, date.dayOfMonth)
        val next = date.plusDays(1)
        val from = "%04d-%02d-%02d 00:00:00+00".format(date.year, date.monthValue, date.dayOfMonth)
        val to = "%04d-%02d-%02d 00:00:00+00".format(next.year, next.monthValue, next.dayOfMonth)

        transaction {
            // FROM(포함) ~ TO(제외) 반열린 구간. 하루치를 담는 자식 파티션.
            exec("CREATE TABLE IF NOT EXISTS $table PARTITION OF metrics " +
                    "FOR VALUES FROM ('$from') TO ('$to')")
        }
        ensuredDates.add(date)
        log.info("partition ready: {}", table)
    }

    // 한 스냅샷(여러 지표)을 한 트랜잭션으로 저장한다.
    fun save(snapshot: MetricSnapshot) {
        val instant = Instant.ofEpochSecond(snapshot.ts)
        val date = instant.atZone(ZoneOffset.UTC).toLocalDate()
        ensurePartition(date)

        transaction {
            for (metric in snapshot.metrics) {
                MetricsTable.insert {
                    it[ts] = instant
                    it[host] = snapshot.host
                    it[name] = metric.name
                    it[value] = metric.value
                }
            }
        }
    }
}