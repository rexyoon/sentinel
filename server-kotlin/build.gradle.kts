// Ktor(Netty) 서버 + Phase 2에서 추가된 자체 TCP 지표 수신부.
plugins {
    kotlin("jvm") version "1.9.24"
    // JSON 직렬화: @Serializable 데이터 클래스 ↔ JSON 변환 코드를 컴파일 타임에 생성.
    kotlin("plugin.serialization") version "1.9.24"
    application
}

group = "com.sentinel"
version = "0.1.0"

repositories {
    mavenCentral()
}

val ktorVersion = "2.3.12"

dependencies {
    implementation("io.ktor:ktor-server-core:$ktorVersion")
    implementation("io.ktor:ktor-server-netty:$ktorVersion")
    // ktor-network: 코루틴 기반 raw TCP 소켓 (HTTP가 아닌 자체 프로토콜 수신용).
    implementation("io.ktor:ktor-network:$ktorVersion")
    // kotlinx.serialization: 프레임 본문 JSON 파싱.
    implementation("org.jetbrains.kotlinx:kotlinx-serialization-json:1.6.3")

    // ── Phase 3: 저장 ──
    // Exposed: Kotlin ORM. exposed-jdbc(실행) + java-time(timestamp 매핑)까지.
    val exposedVersion = "0.50.1"
    implementation("org.jetbrains.exposed:exposed-core:$exposedVersion")
    implementation("org.jetbrains.exposed:exposed-jdbc:$exposedVersion")
    implementation("org.jetbrains.exposed:exposed-java-time:$exposedVersion")
    implementation("org.postgresql:postgresql:42.7.3")   // JDBC 드라이버
    implementation("com.zaxxer:HikariCP:5.1.0")           // 커넥션 풀
    implementation("redis.clients:jedis:5.1.0")           // Redis 최신값 캐시

    // Ktor는 SLF4J로 로그를 남긴다. 구현체(logback)가 없으면 로그가 통째로 사라진다.
    implementation("ch.qos.logback:logback-classic:1.4.14")

    testImplementation(kotlin("test"))
    testImplementation("io.ktor:ktor-server-test-host:$ktorVersion")
}

kotlin {
    jvmToolchain(17)
}

application {
    mainClass.set("com.sentinel.ApplicationKt")
}
