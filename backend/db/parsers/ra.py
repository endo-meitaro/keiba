"""RA: レース詳細情報 (JV-Data仕様書 V4.8 / 960バイト)"""
from .base import ab, sj, ni, race_header, COURSE_TYPE_MAP, WEATHER_MAP, TRACK_MAP
from typing import Optional


# ── フィールドバイト位置 (0-indexed) ────────────────────
# レース名本題: [26:62] 36bytes (18文字 Shift-JIS)
# レース名副題: [62:98]
# レース名カナ: [98:134]
# レース名略称10文字: [134:144]
# 重賞回次6bytes: [144:150]
# 競走記号(1-3): [150:153]
# 重量種別: [153:154]
# 競走条件コード: [154:160]
# グレード: [160:161]
# トラック種別: [161:162]  1=芝 2=ダート 3=障害
# 距離: [162:166]
# コース: [166:167]  1=左 2=右 3=直線 4=直障
# 天候コード: [167:168]
# 芝馬場状態: [168:169]
# ダート馬場状態: [169:170]
# 発走時刻(HHMM): [170:174]
# 頭数: [183:185]

_RACE_NAME   = (26,  62)
_GRADE       = (160, 161)
_COURSE_TYPE = (161, 162)
_DISTANCE    = (162, 166)
_DIRECTION   = (166, 167)
_WEATHER     = (167, 168)
_TRACK_SHIBA = (168, 169)
_TRACK_DIRT  = (169, 170)
_HEAD_COUNT  = (183, 185)


def parse(data: bytes) -> Optional[dict]:
    if len(data) < 200 or ab(data, 0, 2) != "RA":
        return None

    hdr = race_header(data)
    course_type = ab(data, *_COURSE_TYPE)

    return {
        **hdr,
        "race_name":   sj(data, *_RACE_NAME),
        "grade":       ab(data, *_GRADE),
        "course_type": course_type,
        "course_name": COURSE_TYPE_MAP.get(course_type, ""),
        "distance":    ni(data, *_DISTANCE),
        "direction":   ab(data, *_DIRECTION),
        "weather":     ab(data, *_WEATHER),
        "track_shiba": ab(data, *_TRACK_SHIBA),
        "track_dirt":  ab(data, *_TRACK_DIRT),
        "head_count":  ni(data, *_HEAD_COUNT),
    }
