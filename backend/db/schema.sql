-- ============================================================
--  競馬AI  PostgreSQL スキーマ
--  JV-Data レコード種別: RA SE HR O1 UM KS CK HC DM TM WH WE AS HN SK CS
-- ============================================================

-- RA: レース詳細情報
CREATE TABLE IF NOT EXISTS races (
    race_id          VARCHAR(12) PRIMARY KEY,
    kaisai_date      DATE,
    place_code       VARCHAR(2),
    place_name       VARCHAR(10),
    kaiji            SMALLINT,
    nichiji          SMALLINT,
    race_num         SMALLINT,
    race_name        VARCHAR(60),
    grade            VARCHAR(3),
    course_type      VARCHAR(1),   -- 1=芝 2=ダート 3=障害
    distance         SMALLINT,
    direction        VARCHAR(1),   -- 1=左 2=右 3=直線 4=直障
    weather          VARCHAR(1),
    track_shiba      VARCHAR(1),   -- 芝馬場状態
    track_dirt       VARCHAR(1),   -- ダート馬場状態
    head_count       SMALLINT,
    created_at       TIMESTAMP DEFAULT NOW()
);

-- SE: 馬毎レース情報（成績）
CREATE TABLE IF NOT EXISTS horse_results (
    id               SERIAL PRIMARY KEY,
    race_id          VARCHAR(12) REFERENCES races(race_id) ON DELETE CASCADE,
    umaban           SMALLINT,
    frame            SMALLINT,
    horse_code       VARCHAR(10),
    ijo_kubun        VARCHAR(1),   -- 0=正常 1=取消 2=除外 3=中止 4=失格
    finish_pos       SMALLINT,
    finish_time_raw  VARCHAR(6),   -- MMSSTT (分秒1/10)
    finish_time_sec  NUMERIC(7,1),
    corner_1         SMALLINT,
    corner_2         SMALLINT,
    corner_3         SMALLINT,
    corner_4         SMALLINT,
    odds             NUMERIC(7,1),
    popular_order    SMALLINT,
    jockey_code      VARCHAR(5),
    trainer_code     VARCHAR(5),
    weight           SMALLINT,
    weight_diff      SMALLINT,
    UNIQUE (race_id, umaban)
);

-- UM: 馬基本情報
CREATE TABLE IF NOT EXISTS horses (
    horse_code       VARCHAR(10) PRIMARY KEY,
    horse_name       VARCHAR(36),
    horse_name_kana  VARCHAR(36),
    sex_code         VARCHAR(1),   -- 1=牡 2=牝 3=セン
    birth_date       DATE,
    father_code      VARCHAR(10),
    mother_code      VARCHAR(10),
    updated_at       TIMESTAMP DEFAULT NOW()
);

-- KS: 騎手マスタ
CREATE TABLE IF NOT EXISTS jockeys (
    jockey_code      VARCHAR(5) PRIMARY KEY,
    jockey_name      VARCHAR(34),
    jockey_name_kana VARCHAR(34),
    birth_date       DATE
);

-- TM: 調教師マスタ
CREATE TABLE IF NOT EXISTS trainers (
    trainer_code      VARCHAR(5) PRIMARY KEY,
    trainer_name      VARCHAR(34),
    trainer_name_kana VARCHAR(34),
    birth_date        DATE,
    belong_code       VARCHAR(1)   -- 1=美浦 2=栗東 6=地方 9=外国
);

-- WH: 馬体重
CREATE TABLE IF NOT EXISTS horse_weights (
    race_id          VARCHAR(12),
    umaban           SMALLINT,
    weight           SMALLINT,
    weight_diff      SMALLINT,
    PRIMARY KEY (race_id, umaban)
);

-- HR: 払戻情報
CREATE TABLE IF NOT EXISTS payouts (
    id               SERIAL PRIMARY KEY,
    race_id          VARCHAR(12),
    bet_type         VARCHAR(4),
    combination      VARCHAR(30),
    payout           INTEGER,
    popularity       SMALLINT
);

-- O1: 単勝・複勝オッズ
CREATE TABLE IF NOT EXISTS odds_tanpuku (
    race_id          VARCHAR(12),
    umaban           SMALLINT,
    win_odds         NUMERIC(7,1),
    place_min        NUMERIC(7,1),
    place_max        NUMERIC(7,1),
    PRIMARY KEY (race_id, umaban)
);

-- CK: 調教タイム
CREATE TABLE IF NOT EXISTS training_times (
    id               SERIAL PRIMARY KEY,
    horse_code       VARCHAR(10),
    training_date    DATE,
    place_code       VARCHAR(2),
    training_type    VARCHAR(2),
    course_code      VARCHAR(2),
    lap_time_f4      SMALLINT,    -- 4ハロン (1/10秒)
    lap_time_f3      SMALLINT,    -- 3ハロン
    lap_time_f2      SMALLINT,    -- 2ハロン
    lap_time_f1      SMALLINT,    -- 1ハロン
    time_finish      SMALLINT     -- ラスト1ハロン
);

-- WE: 気象情報
CREATE TABLE IF NOT EXISTS weather_info (
    race_id          VARCHAR(12) PRIMARY KEY,
    weather          VARCHAR(1),
    track_shiba      VARCHAR(1),
    track_dirt       VARCHAR(1),
    recorded_at      TIMESTAMP
);

-- CS: コースマスタ
CREATE TABLE IF NOT EXISTS courses (
    place_code       VARCHAR(2),
    course_type      VARCHAR(1),
    distance         SMALLINT,
    direction        VARCHAR(1),
    PRIMARY KEY (place_code, course_type, distance)
);

-- AS: 産駒別父馬成績
CREATE TABLE IF NOT EXISTS sire_stats (
    father_code      VARCHAR(10),
    course_type      VARCHAR(1),
    distance_type    VARCHAR(2),
    wins             SMALLINT,
    runs             SMALLINT,
    PRIMARY KEY (father_code, course_type, distance_type)
);

-- HC: 馬コード変更
CREATE TABLE IF NOT EXISTS horse_code_changes (
    id               SERIAL PRIMARY KEY,
    old_horse_code   VARCHAR(10),
    new_horse_code   VARCHAR(10),
    change_date      DATE
);

-- DM: 生産者マスタ
CREATE TABLE IF NOT EXISTS breeders (
    breeder_code     VARCHAR(6) PRIMARY KEY,
    breeder_name     VARCHAR(72)
);

-- HN: 馬名変更
CREATE TABLE IF NOT EXISTS horse_name_changes (
    id               SERIAL PRIMARY KEY,
    horse_code       VARCHAR(10),
    new_name         VARCHAR(36),
    change_date      DATE
);

-- SK: 騎手変更
CREATE TABLE IF NOT EXISTS jockey_changes (
    id               SERIAL PRIMARY KEY,
    race_id          VARCHAR(12),
    umaban           SMALLINT,
    old_jockey_code  VARCHAR(5),
    new_jockey_code  VARCHAR(5)
);

-- ── インデックス ──────────────────────────────────────────
CREATE INDEX IF NOT EXISTS idx_horse_results_race      ON horse_results(race_id);
CREATE INDEX IF NOT EXISTS idx_horse_results_horse     ON horse_results(horse_code);
CREATE INDEX IF NOT EXISTS idx_horse_results_jockey    ON horse_results(jockey_code);
CREATE INDEX IF NOT EXISTS idx_races_date              ON races(kaisai_date);
CREATE INDEX IF NOT EXISTS idx_races_place             ON races(place_code);
CREATE INDEX IF NOT EXISTS idx_training_horse          ON training_times(horse_code, training_date);
CREATE INDEX IF NOT EXISTS idx_payouts_race            ON payouts(race_id);
