from pydantic import BaseModel
from typing import List


class HorseEntry(BaseModel):
    umaban: int
    frame: int
    horse_name: str
    jockey: str
    trainer: str
    age: str
    weight: float
    odds: float
    recent_form: str  # 直近5走の着順文字列 例: "11231"（新→旧）


class RaceSummary(BaseModel):
    race_id: str
    race_name: str
    date: str
    place: str
    course_type: str  # 芝 / ダート
    distance: int


class Race(RaceSummary):
    weather: str
    track_condition: str
    entries: List[HorseEntry]


class PredictionEntry(BaseModel):
    umaban: int
    horse_name: str
    score: float
    rank: int
    win_probability: float


class PredictionResult(BaseModel):
    race_id: str
    predictions: List[PredictionEntry]


class BettingTicket(BaseModel):
    bet_type: str  # 単勝 / 馬単 / 三連単
    combination: List[int]  # 馬番のリスト（順番あり）
    score: float


class BettingResult(BaseModel):
    race_id: str
    tansho: List[BettingTicket]
    umatan: List[BettingTicket]
    sanrentan: List[BettingTicket]
