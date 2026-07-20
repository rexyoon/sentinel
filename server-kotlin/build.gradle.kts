// Phase 0: Ktor(Netty) 최소 구성. /health 하나만 서빙한다.
// 왜 의존성을 이렇게 적게 잡았나: 학습 목적상 "지금 필요한 것"만 넣고,
// DB(Exposed)/직렬화(kotlinx.serialization)는 실제로 쓰는 Phase에서 추가한다.
plugins {
    kotlin("jvm") version "1.9.24"
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
