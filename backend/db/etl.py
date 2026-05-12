"""
JV-Link → PostgreSQL ETL スクリプト

使い方:
    cd backend
    python -m db.etl --from 20240101 --option 2

オプション:
    --from   YYYYMMDD  取得開始日 (default: 20200101)
    --option 1=差分  2=全件(初回) 3=蓄積  (default: 2)
    --sid    JV-Link ソフトウェアID (未指定時は config.py の値を使用)
"""
import argparse
import sys
import traceback
from psycopg2.extras import execute_values

import config
from db.connection import transaction, apply_schema
from db.parsers import ra, se, um, ks, tm, wh, hr, o1
from db.parsers.misc import (
    parse_ck, parse_hc, parse_dm, parse_we,
    parse_as, parse_hn, parse_sk, parse_cs,
)

# JV-Data で取得するレコード種別を結合した文字列
DATASPEC = "RASEUMHRO1KSCKHCDMTMWHWEASHNSK"

COUNTER = {k: 0 for k in [
    "RA", "SE", "HR", "O1", "UM", "KS", "CK",
    "HC", "DM", "TM", "WH", "WE", "AS", "HN", "SK", "CS",
    "SKIP", "ERROR",
]}


def upsert_race(cur, d: dict):
    cur.execute("""
        INSERT INTO races (
            race_id, kaisai_date, place_code, place_name,
            kaiji, nichiji, race_num, race_name,
            grade, course_type, distance, direction,
            weather, track_shiba, track_dirt, head_count
        ) VALUES (
            %(race_id)s, %(kaisai_date)s, %(place_code)s, %(place_name)s,
            %(kaiji)s, %(nichiji)s, %(race_num)s, %(race_name)s,
            %(grade)s, %(course_type)s, %(distance)s, %(direction)s,
            %(weather)s, %(track_shiba)s, %(track_dirt)s, %(head_count)s
        )
        ON CONFLICT (race_id) DO UPDATE SET
            race_name      = EXCLUDED.race_name,
            grade          = EXCLUDED.grade,
            course_type    = EXCLUDED.course_type,
            distance       = EXCLUDED.distance,
            weather        = EXCLUDED.weather,
            track_shiba    = EXCLUDED.track_shiba,
            track_dirt     = EXCLUDED.track_dirt,
            head_count     = EXCLUDED.head_count
    """, d)


def upsert_horse_result(cur, d: dict):
    cur.execute("""
        INSERT INTO horse_results (
            race_id, umaban, frame, horse_code, ijo_kubun,
            finish_pos, finish_time_raw, finish_time_sec,
            corner_1, corner_2, corner_3, corner_4,
            odds, popular_order, jockey_code, trainer_code,
            weight, weight_diff
        ) VALUES (
            %(race_id)s, %(umaban)s, %(frame)s, %(horse_code)s, %(ijo_kubun)s,
            %(finish_pos)s, %(finish_time_raw)s, %(finish_time_sec)s,
            %(corner_1)s, %(corner_2)s, %(corner_3)s, %(corner_4)s,
            %(odds)s, %(popular_order)s, %(jockey_code)s, %(trainer_code)s,
            %(weight)s, %(weight_diff)s
        )
        ON CONFLICT (race_id, umaban) DO UPDATE SET
            finish_pos      = EXCLUDED.finish_pos,
            finish_time_sec = EXCLUDED.finish_time_sec,
            odds            = EXCLUDED.odds,
            popular_order   = EXCLUDED.popular_order,
            weight          = EXCLUDED.weight,
            weight_diff     = EXCLUDED.weight_diff
    """, d)


def dispatch(cur, record_type: str, data: bytes):
    """レコード種別ごとに対応するパーサーとINSERTを呼び出す"""
    if record_type == "RA":
        d = ra.parse(data)
        if d:
            upsert_race(cur, d)

    elif record_type == "SE":
        d = se.parse(data)
        if d:
            upsert_horse_result(cur, d)

    elif record_type == "WH":
        d = wh.parse(data)
        if d:
            cur.execute("""
                INSERT INTO horse_weights (race_id, umaban, weight, weight_diff)
                VALUES (%(race_id)s, %(umaban)s, %(weight)s, %(weight_diff)s)
                ON CONFLICT (race_id, umaban) DO UPDATE SET
                    weight = EXCLUDED.weight, weight_diff = EXCLUDED.weight_diff
            """, d)

    elif record_type == "HR":
        rows = hr.parse(data)
        if rows:
            for r in rows:
                cur.execute("""
                    INSERT INTO payouts (race_id, bet_type, combination, payout, popularity)
                    VALUES (%(race_id)s, %(bet_type)s, %(combination)s, %(payout)s, %(popularity)s)
                """, r)

    elif record_type == "O1":
        rows = o1.parse(data)
        if rows:
            for r in rows:
                cur.execute("""
                    INSERT INTO odds_tanpuku (race_id, umaban, win_odds, place_min, place_max)
                    VALUES (%(race_id)s, %(umaban)s, %(win_odds)s, %(place_min)s, %(place_max)s)
                    ON CONFLICT (race_id, umaban) DO UPDATE SET
                        win_odds = EXCLUDED.win_odds,
                        place_min = EXCLUDED.place_min,
                        place_max = EXCLUDED.place_max
                """, r)

    elif record_type == "UM":
        d = um.parse(data)
        if d:
            cur.execute("""
                INSERT INTO horses (horse_code, horse_name, horse_name_kana,
                    sex_code, birth_date, father_code, mother_code)
                VALUES (%(horse_code)s, %(horse_name)s, %(horse_name_kana)s,
                    %(sex_code)s, %(birth_date)s, %(father_code)s, %(mother_code)s)
                ON CONFLICT (horse_code) DO UPDATE SET
                    horse_name = EXCLUDED.horse_name
            """, d)

    elif record_type == "KS":
        d = ks.parse(data)
        if d:
            cur.execute("""
                INSERT INTO jockeys (jockey_code, jockey_name, jockey_name_kana, birth_date)
                VALUES (%(jockey_code)s, %(jockey_name)s, %(jockey_name_kana)s, %(birth_date)s)
                ON CONFLICT (jockey_code) DO UPDATE SET jockey_name = EXCLUDED.jockey_name
            """, d)

    elif record_type == "TM":
        d = tm.parse(data)
        if d:
            cur.execute("""
                INSERT INTO trainers (trainer_code, trainer_name, trainer_name_kana,
                    birth_date, belong_code)
                VALUES (%(trainer_code)s, %(trainer_name)s, %(trainer_name_kana)s,
                    %(birth_date)s, %(belong_code)s)
                ON CONFLICT (trainer_code) DO UPDATE SET trainer_name = EXCLUDED.trainer_name
            """, d)

    elif record_type == "CK":
        d = parse_ck(data)
        if d:
            cur.execute("""
                INSERT INTO training_times (horse_code, training_date, place_code,
                    training_type, course_code, lap_time_f4, lap_time_f3,
                    lap_time_f2, lap_time_f1, time_finish)
                VALUES (%(horse_code)s, %(training_date)s, %(place_code)s,
                    %(training_type)s, %(course_code)s, %(lap_f4)s, %(lap_f3)s,
                    %(lap_f2)s, %(lap_f1)s, %(time_finish)s)
            """, d)

    elif record_type == "HC":
        d = parse_hc(data)
        if d:
            cur.execute("""
                INSERT INTO horse_code_changes (old_horse_code, new_horse_code, change_date)
                VALUES (%(old_horse_code)s, %(new_horse_code)s, %(change_date)s)
            """, d)

    elif record_type == "DM":
        d = parse_dm(data)
        if d:
            cur.execute("""
                INSERT INTO breeders (breeder_code, breeder_name)
                VALUES (%(breeder_code)s, %(breeder_name)s)
                ON CONFLICT (breeder_code) DO UPDATE SET breeder_name = EXCLUDED.breeder_name
            """, d)

    elif record_type == "WE":
        d = parse_we(data)
        if d:
            cur.execute("""
                INSERT INTO weather_info (race_id, weather, track_shiba, track_dirt)
                VALUES (%(race_id)s, %(weather)s, %(track_shiba)s, %(track_dirt)s)
                ON CONFLICT (race_id) DO UPDATE SET
                    weather = EXCLUDED.weather,
                    track_shiba = EXCLUDED.track_shiba,
                    track_dirt = EXCLUDED.track_dirt
            """, d)

    elif record_type == "AS":
        d = parse_as(data)
        if d:
            cur.execute("""
                INSERT INTO sire_stats (father_code, course_type, distance_type, wins, runs)
                VALUES (%(father_code)s, %(course_type)s, %(distance_type)s, %(wins)s, %(runs)s)
                ON CONFLICT (father_code, course_type, distance_type) DO UPDATE SET
                    wins = EXCLUDED.wins, runs = EXCLUDED.runs
            """, d)

    elif record_type == "HN":
        d = parse_hn(data)
        if d:
            cur.execute("""
                INSERT INTO horse_name_changes (horse_code, new_name, change_date)
                VALUES (%(horse_code)s, %(new_name)s, %(change_date)s)
            """, d)

    elif record_type == "SK":
        d = parse_sk(data)
        if d:
            cur.execute("""
                INSERT INTO jockey_changes (race_id, umaban, old_jockey_code, new_jockey_code)
                VALUES (%(race_id)s, %(umaban)s, %(old_jockey_code)s, %(new_jockey_code)s)
            """, d)

    elif record_type == "CS":
        d = parse_cs(data)
        if d:
            cur.execute("""
                INSERT INTO courses (place_code, course_type, distance, direction)
                VALUES (%(place_code)s, %(course_type)s, %(distance)s, %(direction)s)
                ON CONFLICT (place_code, course_type, distance) DO UPDATE SET
                    direction = EXCLUDED.direction
            """, d)

    else:
        COUNTER["SKIP"] += 1
        return

    COUNTER[record_type] = COUNTER.get(record_type, 0) + 1


def run_etl(sid: str, from_date: str, option: int):
    try:
        import win32com.client
    except ImportError:
        print("❌ pywin32 が見つかりません: pip install pywin32")
        sys.exit(1)

    print(f"JV-Link に接続中 (SID={sid or '(空)'}) ...")
    jv = win32com.client.Dispatch("JVDTLab.JVLink")

    ret = jv.JVInit(sid)
    if ret != 0:
        print(f"❌ JVInit 失敗: ret={ret}  SIDを確認してください")
        sys.exit(1)

    from_time = f"{from_date}000000"
    ret, total, last_file, last_time = jv.JVOpen(DATASPEC, from_time, option)
    if ret < 0:
        print(f"❌ JVOpen 失敗: ret={ret}")
        jv.JVClose()
        sys.exit(1)

    print(f"✅ JVOpen 完了: 総ファイル数={total}  取得開始時刻={last_time}")

    # スキーマ作成
    apply_schema()

    processed = 0
    BATCH     = 500

    with transaction() as conn:
        cur = conn.cursor()

        while True:
            ret, buff, filename = jv.JVRead()

            if ret == 0:
                break
            if ret == -1:
                # ファイル区切り: 次のファイルへ
                continue
            if ret < -1:
                print(f"⚠ JVRead エラー: ret={ret}")
                COUNTER["ERROR"] += 1
                break

            try:
                data        = buff.encode("shift-jis", errors="replace") if isinstance(buff, str) else buff
                record_type = data[0:2].decode("ascii", errors="ignore")
                dispatch(cur, record_type, data)
            except Exception:
                COUNTER["ERROR"] += 1

            processed += 1
            if processed % BATCH == 0:
                conn.commit()
                print(f"  {processed:,} 件処理済み ...", end="\r")

        conn.commit()

    jv.JVClose()

    print(f"\n✅ ETL 完了: 合計 {processed:,} レコード")
    for k, v in COUNTER.items():
        if v:
            print(f"   {k}: {v:,}")


def main():
    parser = argparse.ArgumentParser(description="JV-Data → PostgreSQL ETL")
    parser.add_argument("--from",   dest="from_date", default="20200101")
    parser.add_argument("--option", type=int,         default=2)
    parser.add_argument("--sid",    default=config.JVLINK_SID)
    args = parser.parse_args()

    if not args.sid:
        print("⚠ SID が未設定です。backend/config.py の JVLINK_SID を設定するか")
        print("   環境変数 JVLINK_SID に JRA-VAN マイページのソフトウェアIDを設定してください。")
        sys.exit(1)

    run_etl(args.sid, args.from_date, args.option)


if __name__ == "__main__":
    main()
