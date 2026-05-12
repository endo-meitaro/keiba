from fastapi import APIRouter, HTTPException

from models.schemas import PredictionResult
from services.data_source import DataSource
from services.predictor import Predictor

router = APIRouter()
_predictor = Predictor()


def get_router(ds: DataSource) -> APIRouter:

    @router.get("/{race_id}/prediction", response_model=PredictionResult)
    def predict(race_id: str):
        try:
            race = ds.get_race(race_id)
        except KeyError as e:
            raise HTTPException(status_code=404, detail=str(e))
        return _predictor.predict(race)

    return router
