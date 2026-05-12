"""TM: 調教師マスタ"""
from .base import ab, sj, parse_date8, BELONG_MAP
from typing import Optional


_TRAINER_CODE = (10, 15)
_TRAINER_NAME = (15, 49)
_TRAINER_KANA = (49, 83)
_BIRTH_DATE   = (83, 91)
_BELONG_CODE  = (91, 92)  # 1=美浦 2=栗東


def parse(data: bytes) -> Optional[dict]:
    if len(data) < 95 or ab(data, 0, 2) != "TM":
        return None
    bc = ab(data, *_BELONG_CODE)
    return {
        "trainer_code":      ab(data, *_TRAINER_CODE),
        "trainer_name":      sj(data, *_TRAINER_NAME),
        "trainer_name_kana": sj(data, *_TRAINER_KANA),
        "birth_date":        parse_date8(ab(data, *_BIRTH_DATE)),
        "belong_code":       bc,
        "belong_name":       BELONG_MAP.get(bc, ""),
    }
