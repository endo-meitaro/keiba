"""WH: 馬体重"""
from .base import ab, ni, race_header
from typing import Optional


_UMABAN      = (26, 28)
_WEIGHT      = (28, 31)
_WEIGHT_DIFF = (31, 35)  # 符号付き (+nnn / -nnn)


def parse(data: bytes) -> Optional[dict]:
    if len(data) < 36 or ab(data, 0, 2) != "WH":
        return None

    hdr       = race_header(data)
    wdiff_raw = ab(data, *_WEIGHT_DIFF)
    try:
        weight_diff = int(wdiff_raw)
    except ValueError:
        weight_diff = None

    return {
        "race_id":     hdr["race_id"],
        "umaban":      ni(data, *_UMABAN),
        "weight":      ni(data, *_WEIGHT),
        "weight_diff": weight_diff,
    }
