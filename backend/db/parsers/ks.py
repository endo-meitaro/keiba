"""KS: 騎手マスタ"""
from .base import ab, sj, parse_date8
from typing import Optional


_JOCKEY_CODE = (10, 15)
_JOCKEY_NAME = (15, 49)   # 34bytes Shift-JIS
_JOCKEY_KANA = (49, 83)   # 34bytes
_BIRTH_DATE  = (83, 91)   # YYYYMMDD


def parse(data: bytes) -> Optional[dict]:
    if len(data) < 95 or ab(data, 0, 2) != "KS":
        return None
    return {
        "jockey_code":      ab(data, *_JOCKEY_CODE),
        "jockey_name":      sj(data, *_JOCKEY_NAME),
        "jockey_name_kana": sj(data, *_JOCKEY_KANA),
        "birth_date":       parse_date8(ab(data, *_BIRTH_DATE)),
    }
