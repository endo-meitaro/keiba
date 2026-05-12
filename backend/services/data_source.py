from abc import ABC, abstractmethod
from typing import List

from models.schemas import Race, RaceSummary


class DataSource(ABC):
    """データ取得の抽象インターフェース。JRA-VAN接続時はこれを実装して差し替える。"""

    @abstractmethod
    def get_race_list(self, date: str) -> List[RaceSummary]:
        pass

    @abstractmethod
    def get_race(self, race_id: str) -> Race:
        pass


class MockDataSource(DataSource):

    def get_race_list(self, date: str) -> List[RaceSummary]:
        from mock.data import MOCK_RACES
        return [
            RaceSummary(
                race_id=r.race_id,
                race_name=r.race_name,
                date=r.date,
                place=r.place,
                course_type=r.course_type,
                distance=r.distance,
            )
            for r in MOCK_RACES
            if r.date == date
        ]

    def get_race(self, race_id: str) -> Race:
        from mock.data import MOCK_RACES
        race = next((r for r in MOCK_RACES if r.race_id == race_id), None)
        if race is None:
            raise KeyError(f"race_id={race_id} が見つかりません")
        return race
