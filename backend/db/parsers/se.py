"""SE: 馬毎レース情報 (JV-Data仕様書 V4.8 / 612バイト)"""
from .base import ab, sj, ni, nf, race_header
from typing import Optional


# ── フィールドバイト位置 (0-indexed) ────────────────────
# [26:28] 馬番
# [28:29] 枠番
# [29:39] 馬コード (10桁)
# [39:40] 異常区分 0=正常 1=取消 2=除外 3=中止 4=失格
# [40:42] 着順 (00=除外等)
# [42:48] タイム (MMSSTT: 分・秒・1/10秒)
# [48:52] 着差コード
# [52:56] コーナー順位1〜4 各1byte
# [56:62] 単勝オッズ (999.9倍 = "9999" × 0.1)
# [62:64] 人気順
# [64:69] 騎手コード
# [69:74] 調教師コード
# [74:77] 馬体重
# [77:80] 馬体重増減 (+nnn or -nnn → 符号付き3桁)

_UMABAN      = (26, 28)
_FRAME       = (28, 29)
_HORSE_CODE  = (29, 39)
_IJO         = (39, 40)
_FINISH_POS  = (40, 42)
_TIME_RAW    = (42, 48)
_CORNER_1    = (52, 53)
_CORNER_2    = (53, 54)
_CORNER_3    = (54, 55)
_CORNER_4    = (55, 56)
_ODDS        = (56, 60)   # ×0.1
_POPULAR     = (60, 62)
_JOCKEY      = (62, 67)
_TRAINER     = (67, 72)
_WEIGHT      = (72, 75)
_WEIGHT_DIFF = (75, 79)


def _time_to_sec(raw: str) -> Optional[float]:
    """MMSSTT → 秒 (float)"""
    if len(raw) < 6 or not raw.isdigit():
        return None
    mm, ss, tt = int(raw[0:2]), int(raw[2:4]), int(raw[4:6])
    return mm * 60 + ss + tt / 10


def parse(data: bytes) -> Optional[dict]:
    if len(data) < 80 or ab(data, 0, 2) != "SE":
        return None

    hdr       = race_header(data)
    time_raw  = ab(data, *_TIME_RAW)
    odds_raw  = ab(data, *_ODDS)
    wdiff_raw = ab(data, *_WEIGHT_DIFF)

    try:
        weight_diff = int(wdiff_raw)
    except ValueError:
        weight_diff = None

    return {
        **hdr,
        "umaban":          ni(data, *_UMABAN),
        "frame":           ni(data, *_FRAME),
        "horse_code":      ab(data, *_HORSE_CODE),
        "ijo_kubun":       ab(data, *_IJO),
        "finish_pos":      ni(data, *_FINISH_POS),
        "finish_time_raw": time_raw,
        "finish_time_sec": _time_to_sec(time_raw),
        "corner_1":        ni(data, *_CORNER_1),
        "corner_2":        ni(data, *_CORNER_2),
        "corner_3":        ni(data, *_CORNER_3),
        "corner_4":        ni(data, *_CORNER_4),
        "odds":            int(odds_raw) / 10.0 if odds_raw.isdigit() else None,
        "popular_order":   ni(data, *_POPULAR),
        "jockey_code":     ab(data, *_JOCKEY),
        "trainer_code":    ab(data, *_TRAINER),
        "weight":          ni(data, *_WEIGHT),
        "weight_diff":     weight_diff,
    }
