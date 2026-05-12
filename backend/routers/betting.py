from fastapi import APIRouter, HTTPException

from models.schemas import BettingResult
from services.data_source import DataSource
from services.predictor import Predictor
from services.betting_service import BettingService

router = APIRouter()
_predictor = Predictor()
_betting = BettingService()


def get_router(ds: DataSource) -> APIRouter:

    @router.get("/{race_id}/betting", response_model=BettingResult)
    def betting(race_id: str):
        try:
            race = ds.get_race(race_id)
        except KeyError as e:
            raise HTTPException(status_code=404, detail=str(e))
        prediction = _predictor.predict(race)
        return _betting.generate(prediction)

    return router
