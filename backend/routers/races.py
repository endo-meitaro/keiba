from fastapi import APIRouter, HTTPException, Query
from typing import List

from models.schemas import RaceSummary, Race
from services.data_source import DataSource

router = APIRouter()


def get_router(ds: DataSource) -> APIRouter:

    @router.get("", response_model=List[RaceSummary])
    def list_races(date: str = Query(..., description="開催日 YYYYMMDD")):
        return ds.get_race_list(date)

    @router.get("/{race_id}", response_model=Race)
    def get_race(race_id: str):
        try:
            return ds.get_race(race_id)
        except KeyError as e:
            raise HTTPException(status_code=404, detail=str(e))

    return router
