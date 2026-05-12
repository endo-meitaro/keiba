from itertools import permutations

from models.schemas import BettingTicket, BettingResult, PredictionResult


class BettingService:
    """予測スコアをもとに単勝・馬単・三連単の買い目を生成する。"""

    TANSHO_COUNT = 3
    UMATAN_COUNT = 6
    SANRENTAN_COUNT = 10
    TOP_N = 4  # 馬単・三連単の組み合わせに使う上位馬数

    def generate(self, prediction: PredictionResult) -> BettingResult:
        ranked = sorted(prediction.predictions, key=lambda p: p.rank)

        # 単勝
        tansho = [
            BettingTicket(
                bet_type="単勝",
                combination=[p.umaban],
                score=round(p.win_probability, 6),
            )
            for p in ranked[: self.TANSHO_COUNT]
        ]

        top = ranked[: self.TOP_N]

        # 馬単（2頭の順列）
        umatan_candidates = [
            BettingTicket(
                bet_type="馬単",
                combination=[p1.umaban, p2.umaban],
                score=round(p1.win_probability * p2.win_probability, 8),
            )
            for p1, p2 in permutations(top, 2)
        ]
        umatan = sorted(umatan_candidates, key=lambda t: -t.score)[: self.UMATAN_COUNT]

        # 三連単（3頭の順列）
        sanrentan_candidates = [
            BettingTicket(
                bet_type="三連単",
                combination=[p1.umaban, p2.umaban, p3.umaban],
                score=round(
                    p1.win_probability * p2.win_probability * p3.win_probability, 10
                ),
            )
            for p1, p2, p3 in permutations(top, 3)
        ]
        sanrentan = sorted(sanrentan_candidates, key=lambda t: -t.score)[
            : self.SANRENTAN_COUNT
        ]

        return BettingResult(
            race_id=prediction.race_id,
            tansho=tansho,
            umatan=umatan,
            sanrentan=sanrentan,
        )
