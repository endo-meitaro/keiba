"""
JV-Data 固定長バイト列パーサーの共通ユーティリティ。
フィールド位置は JRA-VAN JV-Data仕様書 V4.8 に基づく。
"""
from datetime import date
from typing import Optional


JYOCODE_MAP = {
    "01": "札幌", "02": "函館", "03": "福島", "04": "新潟",
    "05": "東京", "06": "中山", "07": "中京", "08": "京都",
    "09": "阪神", "10": "小倉",
}
COURSE_TYPE_MAP = {"1": "芝", "2": "ダート", "3": "障害"}
WEATHER_MAP     = {"1": "晴", "2": "曇", "3": "雨", "4": "小雨", "5": "雪", "6": "小雪"}
TRACK_MAP       = {"1": "良", "2": "稍重", "3": "重", "4": "不良"}
SEX_MAP         = {"1": "牡", "2": "牝", "3": "セン"}
BELONG_MAP      = {"1": "美浦", "2": "栗東", "6": "地方", "9": "外国"}


def ab(data: bytes, s: int, e: int) -> str:
    """ASCII フィールドを取り出してstrip"""
    return data[s:e].decode("ascii", errors="ignore").strip()

def sj(data: bytes, s: int, e: int) -> str:
    """Shift-JIS テキストフィールドを取り出してstrip"""
    return data[s:e].decode("shift-jis", errors="ignore").strip()

def ni(data: bytes, s: int, e: int) -> Optional[int]:
    """数値フィールドを int に変換。空白 or 非数字は None"""
    v = ab(data, s, e)
    return int(v) if v.lstrip("0") != "" and v.isdigit() else (0 if v == "0" * len(v) else None)

def nf(data: bytes, s: int, e: int, scale: int = 1) -> Optional[float]:
    """数値フィールドを float に変換（scale で割る）"""
    v = ab(data, s, e)
    if not v or not v.lstrip("0") and v != "0" * len(v):
        return None
    try:
        return int(v) / scale
    except ValueError:
        return None

def parse_date(year: str, mmdd: str) -> Optional[date]:
    try:
        return date(int(year), int(mmdd[:2]), int(mmdd[2:]))
    except Exception:
        return None

def parse_date8(val: str) -> Optional[date]:
    """YYYYMMDD 形式を date に変換"""
    try:
        return date(int(val[:4]), int(val[4:6]), int(val[6:8]))
    except Exception:
        return None

def make_race_id(year: str, place: str, kaiji: str, nichiji: str, racenum: str) -> str:
    return f"{year}{place.zfill(2)}{kaiji.zfill(2)}{nichiji.zfill(2)}{racenum.zfill(2)}"

def race_header(data: bytes) -> dict:
    """全レースレコード共通ヘッダー（RA/SE/HR/O1/WH/WE）を解析する"""
    year    = ab(data, 10, 14)
    month   = ab(data, 14, 16)
    day     = ab(data, 16, 18)
    place   = ab(data, 18, 20)
    kaiji   = ab(data, 20, 22)
    nichiji = ab(data, 22, 24)
    racenum = ab(data, 24, 26)
    return {
        "race_id":    make_race_id(year, place, kaiji, nichiji, racenum),
        "kaisai_date": parse_date(year, month + day),
        "place_code": place,
        "place_name": JYOCODE_MAP.get(place, place),
        "kaiji":      int(kaiji)   if kaiji.isdigit()   else None,
        "nichiji":    int(nichiji) if nichiji.isdigit() else None,
        "race_num":   int(racenum) if racenum.isdigit() else None,
    }
