-- Sentinel 지표 저장 스키마 (PostgreSQL 16)
--
-- 핵심: metrics 는 '부모(파티션된) 테이블'이고, 실제 행은 날짜별 자식 파티션에 들어간다.
-- PARTITION BY RANGE (ts): ts 값의 범위(여기선 하루)로 자식 테이블을 나눈다.
--
-- 왜 이렇게 하나 (시계열의 숙명):
--   지표는 초당 수 건씩 무한히 쌓여 금세 수억 행이 된다. 한 테이블에 다 넣으면
--   - 오래된 데이터 삭제가 느리다(대량 DELETE + VACUUM).
--   - 조회 시 전체를 훑을 위험이 있다.
--   날짜별 파티션이면:
--   - 지난 데이터는 파티션을 통째로 DROP → 즉시 삭제(공책째 버리기).
--   - 특정 날짜 조회는 그 파티션만 스캔(partition pruning).

-- ── 부모 테이블 ──
-- 부모에는 데이터가 직접 저장되지 않는다. INSERT 하면 ts 를 보고 알맞은 자식으로 자동 라우팅.
CREATE TABLE IF NOT EXISTS metrics (
    ts     timestamptz      NOT NULL,  -- 수집 시각 (파티션 키)
    host   text             NOT NULL,  -- 지표를 보낸 호스트
    name   text             NOT NULL,  -- 지표 이름 (cpu, mem ...)
    value  double precision NOT NULL   -- 측정값 (0~100 %)
) PARTITION BY RANGE (ts);

-- 부모에 만든 인덱스는 '템플릿'이라, 이후 생기는 모든 자식 파티션에 자동 적용된다.
-- (host, name) 로 필터하고 최신순으로 보는 조회 패턴을 위한 인덱스.
CREATE INDEX IF NOT EXISTS metrics_host_name_ts_idx
    ON metrics (host, name, ts DESC);

-- ── 자식 파티션 예시 (하루치) ──
-- 실제로는 애플리케이션이 매일 필요한 파티션을 자동 생성한다(ensurePartition).
-- 아래는 스키마 이해를 돕기 위한 예시. FROM(포함) ~ TO(제외) 반열린 구간.
--
-- CREATE TABLE IF NOT EXISTS metrics_2026_07_20 PARTITION OF metrics
--     FOR VALUES FROM ('2026-07-20 00:00:00+00') TO ('2026-07-21 00:00:00+00');
