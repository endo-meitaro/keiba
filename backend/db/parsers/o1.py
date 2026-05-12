"""O1: 単勝・複勝オッズ"""
from .base import ab, ni, race_header
from typing import Optional, List


# [26:28] 馬番
# [28:32] 単勝オッズ (×0.1)
# [32:36] 複勝オッズ下限 (×0.1)
# [36:40] 複勝オッズ上限 (×0.1)
# [40:41] 取消フラグ
_ENTRY_LEN = 15  # 1頭分のブロック長
_MAX_HORSES = 18


def parse(data: bytes) -> Optional[List[dict]]:
    if len(data) < 30 or ab(data, 0, 2) != "O1":
        return None

    hdr     = race_header(data)
    race_id = hdr["race_id"]
    results = []
    pos     = 26

    for _ in range(_MAX_HORSES):
        if pos + 15 > len(data):
            break

        umaban_raw   = ab(data, pos,      pos + 2)
        win_raw      = ab(data, pos + 2,  pos + 6)
        place_lo_raw = ab(data, pos + 6,  pos + 10)
        place_hi_raw = ab(data, pos + 10, pos + 14)
        cancel_flag  = ab(data, pos + 14, pos + 15)
        pos += 15

        if not umaban_raw.isdigit() or int(umaban_raw) == 0:
            continue

        def to_odds(s: str) -> Optional[float]:
            return int(s) / 10.0 if s.isdigit() and int(s) > 0 else None

        results.append({
            "race_id":   race_id,
            "umaban":    int(umaban_raw),
            "win_odds":  to_odds(win_raw),
            "place_min": to_odds(place_lo_raw),
            "place_max": to_odds(place_hi_raw),
        })

    return results
