"""HR: 払戻情報"""
from .base import ab, sj, ni, race_header
from typing import Optional, List


# 払戻レコードは各券種ごとに繰り返しブロックを持つ
# [26:] 以降に複数の払戻ブロックが続く
# 各ブロック: 券種コード(2) + 払戻数(2) + [組合せ(20) + 払戻金(8) + 人気(2)] ×n
_BET_TYPES = {
    "01": "単勝", "02": "複勝", "03": "枠連",
    "04": "馬連", "05": "ワイド", "06": "馬単",
    "07": "三連複", "08": "三連単",
}
_BLOCK_START = 26
_TYPE_LEN    = 2
_COUNT_LEN   = 2
_COMB_LEN    = 20
_PAYOUT_LEN  = 8
_POP_LEN     = 2
_ENTRY_LEN   = _COMB_LEN + _PAYOUT_LEN + _POP_LEN  # 30


def parse(data: bytes) -> Optional[List[dict]]:
    if len(data) < 30 or ab(data, 0, 2) != "HR":
        return None

    hdr     = race_header(data)
    race_id = hdr["race_id"]
    results = []
    pos     = _BLOCK_START

    while pos + _TYPE_LEN + _COUNT_LEN <= len(data):
        bet_type_code = ab(data, pos, pos + _TYPE_LEN)
        pos += _TYPE_LEN

        count_str = ab(data, pos, pos + _COUNT_LEN)
        pos += _COUNT_LEN

        if not count_str.isdigit():
            break
        count = int(count_str)

        bet_name = _BET_TYPES.get(bet_type_code, bet_type_code)

        for _ in range(count):
            if pos + _ENTRY_LEN > len(data):
                break
            combination = sj(data, pos, pos + _COMB_LEN)
            payout_raw  = ab(data, pos + _COMB_LEN, pos + _COMB_LEN + _PAYOUT_LEN)
            pop_raw     = ab(data, pos + _COMB_LEN + _PAYOUT_LEN, pos + _ENTRY_LEN)

            try:
                payout     = int(payout_raw)
                popularity = int(pop_raw) if pop_raw.isdigit() else None
            except ValueError:
                payout, popularity = None, None

            results.append({
                "race_id":    race_id,
                "bet_type":   bet_name,
                "combination": combination,
                "payout":     payout,
                "popularity": popularity,
            })
            pos += _ENTRY_LEN

    return results
