"""
CK / HC / DM / WE / AS / HN / SK / CS の各パーサー
"""
from .base import ab, sj, ni, race_header, parse_date8
from typing import Optional, List


# ── CK: 調教タイム ────────────────────────────────────────
# [10:20] 馬コード
# [20:28] 調教年月日 YYYYMMDD
# [28:30] 調教場コード
# [30:32] 調教種別
# [32:34] コースコード
# [34:38] ラップタイムF4 (1/10秒)
# [38:42] ラップタイムF3
# [42:46] ラップタイムF2
# [46:50] ラップタイムF1
# [50:54] ゴールタイム
def parse_ck(data: bytes) -> Optional[dict]:
    if len(data) < 55 or ab(data, 0, 2) != "CK":
        return None
    return {
        "horse_code":    ab(data, 10, 20),
        "training_date": parse_date8(ab(data, 20, 28)),
        "place_code":    ab(data, 28, 30),
        "training_type": ab(data, 30, 32),
        "course_code":   ab(data, 32, 34),
        "lap_f4":        ni(data, 34, 38),
        "lap_f3":        ni(data, 38, 42),
        "lap_f2":        ni(data, 42, 46),
        "lap_f1":        ni(data, 46, 50),
        "time_finish":   ni(data, 50, 54),
    }


# ── HC: 馬コード変更 ──────────────────────────────────────
# [10:18] 変更年月日 YYYYMMDD
# [18:28] 旧馬コード
# [28:38] 新馬コード
def parse_hc(data: bytes) -> Optional[dict]:
    if len(data) < 38 or ab(data, 0, 2) != "HC":
        return None
    return {
        "change_date":   parse_date8(ab(data, 10, 18)),
        "old_horse_code": ab(data, 18, 28),
        "new_horse_code": ab(data, 28, 38),
    }


# ── DM: 生産者マスタ ──────────────────────────────────────
# [10:16] 生産者コード (6桁)
# [16:88] 生産者名 (72bytes Shift-JIS)
def parse_dm(data: bytes) -> Optional[dict]:
    if len(data) < 88 or ab(data, 0, 2) != "DM":
        return None
    return {
        "breeder_code": ab(data,  10, 16),
        "breeder_name": sj(data,  16, 88),
    }


# ── WE: 気象情報 ──────────────────────────────────────────
def parse_we(data: bytes) -> Optional[dict]:
    if len(data) < 30 or ab(data, 0, 2) != "WE":
        return None
    hdr = race_header(data)
    return {
        "race_id":     hdr["race_id"],
        "weather":     ab(data, 26, 27),
        "track_shiba": ab(data, 27, 28),
        "track_dirt":  ab(data, 28, 29),
    }


# ── AS: 産駒別父馬成績 ────────────────────────────────────
# [10:20] 父馬コード
# [20:21] トラック種別
# [21:23] 距離区分
# [23:27] 1着回数
# [27:31] 出走回数
def parse_as(data: bytes) -> Optional[dict]:
    if len(data) < 31 or ab(data, 0, 2) != "AS":
        return None
    return {
        "father_code":   ab(data, 10, 20),
        "course_type":   ab(data, 20, 21),
        "distance_type": ab(data, 21, 23),
        "wins":          ni(data, 23, 27),
        "runs":          ni(data, 27, 31),
    }


# ── HN: 馬名変更 ──────────────────────────────────────────
# [10:18] 変更年月日
# [18:28] 馬コード
# [28:64] 新馬名 (36bytes Shift-JIS)
def parse_hn(data: bytes) -> Optional[dict]:
    if len(data) < 64 or ab(data, 0, 2) != "HN":
        return None
    return {
        "change_date": parse_date8(ab(data, 10, 18)),
        "horse_code":  ab(data, 18, 28),
        "new_name":    sj(data, 28, 64),
    }


# ── SK: 騎手変更 ──────────────────────────────────────────
# race_header (26bytes) の後:
# [26:28] 馬番
# [28:33] 変更前騎手コード
# [33:38] 変更後騎手コード
def parse_sk(data: bytes) -> Optional[dict]:
    if len(data) < 38 or ab(data, 0, 2) != "SK":
        return None
    hdr = race_header(data)
    return {
        "race_id":         hdr["race_id"],
        "umaban":          ni(data, 26, 28),
        "old_jockey_code": ab(data, 28, 33),
        "new_jockey_code": ab(data, 33, 38),
    }


# ── CS: コースマスタ ──────────────────────────────────────
# [10:12] 場コード
# [12:13] トラック種別
# [13:17] 距離
# [17:18] 方向
def parse_cs(data: bytes) -> Optional[dict]:
    if len(data) < 18 or ab(data, 0, 2) != "CS":
        return None
    return {
        "place_code":  ab(data, 10, 12),
        "course_type": ab(data, 12, 13),
        "distance":    ni(data, 13, 17),
        "direction":   ab(data, 17, 18),
    }
