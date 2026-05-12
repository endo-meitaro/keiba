"""UM: 馬基本情報"""
from .base import ab, sj, ni, parse_date8, SEX_MAP
from typing import Optional


_HORSE_CODE   = (10, 20)
_HORSE_NAME   = (20, 56)   # 36bytes Shift-JIS
_HORSE_KANA   = (56, 92)   # 36bytes
_SEX          = (92, 93)
_BIRTH_DATE   = (93, 101)  # YYYYMMDD
_FATHER_CODE  = (101, 111)
_MOTHER_CODE  = (111, 121)


def parse(data: bytes) -> Optional[dict]:
    if len(data) < 125 or ab(data, 0, 2) != "UM":
        return None

    sex = ab(data, *_SEX)
    bd  = parse_date8(ab(data, *_BIRTH_DATE))

    return {
        "horse_code":      ab(data, *_HORSE_CODE),
        "horse_name":      sj(data, *_HORSE_NAME),
        "horse_name_kana": sj(data, *_HORSE_KANA),
        "sex_code":        sex,
        "sex_name":        SEX_MAP.get(sex, ""),
        "birth_date":      bd,
        "father_code":     ab(data, *_FATHER_CODE),
        "mother_code":     ab(data, *_MOTHER_CODE),
    }
