"""
JRAVANDataSource: PostgreSQL からレースデータを取得する DataSource 実装。
DataSource 抽象クラスを継承しており、main.py で MockDataSource と差し替えて使う。
"""
from typing import List
import psycopg2.extras

from models.schemas import Race, RaceSummary, HorseEntry
from services.data_source import DataSource
from db.connection import get_conn


PLACE_NAME = {
    "01": "札幌", "02": "函館", "03": "福島", "04": "新潟",
    "05": "東京", "06": "中山", "07": "中京", "08": "京都",
    "09": "阪神", "10": "小倉",
}
COURSE_NAME = {"1": "芝", "2": "ダート", "3": "障害"}
WEATHER_NAME = {"1": "晴", "2": "曇", "3": "雨", "4": "小雨", "5": "雪", "6": "小雪"}
TRACK_NAME   = {"1": "良", "2": "稍重", "3": "重", "4": "不良"}


class JRAVANDataSource(DataSource):

    def get_race_list(self, date: str) -> List[RaceSummary]:
        """YYYYMMDD 形式の日付でその日のレース一覧を返す"""
        kaisai_date = f"{date[:4]}-{date[4:6]}-{date[6:8]}"
        with get_conn() as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                cur.execute("""
                    SELECT race_id, race_name, kaisai_date, place_code,
                           course_type, distance
                    FROM races
                    WHERE kaisai_date = %s
                    ORDER BY place_code, race_num
                """, (kaisai_date,))
                rows = cur.fetchall()

        return [
            RaceSummary(
                race_id=r["race_id"],
                race_name=r["race_name"] or "（レース名未取得）",
                date=date,
                place=PLACE_NAME.get(r["place_code"], r["place_code"]),
                course_type=COURSE_NAME.get(r["course_type"], ""),
                distance=r["distance"] or 0,
            )
            for r in rows
        ]

    def get_race(self, race_id: str) -> Race:
        with get_conn() as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                # レース情報
                cur.execute("SELECT * FROM races WHERE race_id = %s", (race_id,))
                race_row = cur.fetchone()
                if not race_row:
                    raise KeyError(f"race_id={race_id} が見つかりません")

                # 出走馬一覧（馬体重は horse_weights から補完）
                cur.execute("""
                    SELECT hr.umaban, hr.frame, hr.horse_code,
                           h.horse_name, h.sex_code,
                           j.jockey_name, t.trainer_name,
                           ot.win_odds AS odds,
                           wh.weight, wh.weight_diff,
                           hr.finish_pos
                    FROM horse_results hr
                    LEFT JOIN horses        h  ON h.horse_code   = hr.horse_code
                    LEFT JOIN jockeys       j  ON j.jockey_code  = hr.jockey_code
                    LEFT JOIN trainers      t  ON t.trainer_code = hr.trainer_code
                    LEFT JOIN odds_tanpuku  ot ON ot.race_id = hr.race_id
                                               AND ot.umaban = hr.umaban
                    LEFT JOIN horse_weights wh ON wh.race_id = hr.race_id
                                               AND wh.umaban = hr.umaban
                    WHERE hr.race_id = %s
                    ORDER BY hr.umaban
                """, (race_id,))
                horse_rows = cur.fetchall()

                # 近走成績: 直近5走の着順を文字列化
                horse_codes = [r["horse_code"] for r in horse_rows if r["horse_code"]]
                recent = {}
                if horse_codes:
                    cur.execute("""
                        SELECT hr2.horse_code,
                               STRING_AGG(
                                   CASE WHEN hr2.finish_pos BETWEEN 1 AND 9
                                        THEN hr2.finish_pos::text ELSE '0' END,
                                   '' ORDER BY r2.kaisai_date DESC
                               ) AS form
                        FROM horse_results hr2
                        JOIN races r2 ON r2.race_id = hr2.race_id
                        WHERE hr2.horse_code = ANY(%s)
                          AND r2.kaisai_date < %s
                          AND hr2.ijo_kubun = '0'
                        GROUP BY hr2.horse_code
                    """, (horse_codes, race_row["kaisai_date"]))
                    for row in cur.fetchall():
                        recent[row["horse_code"]] = (row["form"] or "")[:5]

        r = race_row
        date_str = r["kaisai_date"].strftime("%Y%m%d") if r["kaisai_date"] else ""
        ct = r["course_type"] or ""
        track = TRACK_NAME.get(
            r["track_shiba"] if ct == "1" else r["track_dirt"], ""
        )

        entries = [
            HorseEntry(
                umaban      = h["umaban"],
                frame       = h["frame"] or 0,
                horse_name  = h["horse_name"] or "名称不明",
                jockey      = h["jockey_name"] or "不明",
                trainer     = h["trainer_name"] or "不明",
                age         = h["sex_code"] or "",
                weight      = float(h["weight"] or 0),
                odds        = float(h["odds"] or 99.9),
                recent_form = recent.get(h["horse_code"], "00000"),
            )
            for h in horse_rows
        ]

        return Race(
            race_id        = race_id,
            race_name      = r["race_name"] or "（レース名未取得）",
            date           = date_str,
            place          = PLACE_NAME.get(r["place_code"], r["place_code"] or ""),
            course_type    = COURSE_NAME.get(ct, ct),
            distance       = r["distance"] or 0,
            weather        = WEATHER_NAME.get(r["weather"] or "", ""),
            track_condition= track,
            entries        = entries,
        )
