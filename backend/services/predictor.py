from models.schemas import Race, PredictionEntry, PredictionResult


class Predictor:
    """
    オッズと近走成績をもとに各馬のスコアを算出する。
    JRA-VANデータ導入後はここに特徴量エンジニアリングとMLモデルを追加する。
    """

    def _form_score(self, recent_form: str) -> float:
        """直近5走の着順文字列を0-1のスコアに変換する。"""
        points = {1: 5, 2: 4, 3: 3, 4: 2, 5: 2}
        total = 0
        for ch in recent_form[:5]:
            if ch.isdigit():
                pos = int(ch)
                total += points.get(pos, 1 if pos <= 9 else 0)
        return total / 25.0  # 最大25点を正規化

    def predict(self, race: Race) -> PredictionResult:
        scored: list[tuple[int, str, float]] = []

        for entry in race.entries:
            odds_score = 1.0 / entry.odds
            form_score = self._form_score(entry.recent_form)
            raw = 0.65 * odds_score + 0.35 * form_score
            scored.append((entry.umaban, entry.horse_name, raw))

        total = sum(s for _, _, s in scored)
        ranked = sorted(scored, key=lambda x: -x[2])

        predictions = [
            PredictionEntry(
                umaban=umaban,
                horse_name=name,
                score=round(raw, 4),
                rank=rank,
                win_probability=round(raw / total, 4),
            )
            for rank, (umaban, name, raw) in enumerate(ranked, start=1)
        ]

        return PredictionResult(race_id=race.race_id, predictions=predictions)
