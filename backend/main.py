import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from services.data_source import MockDataSource
from services.jravan_source import JRAVANDataSource
from routers import races, prediction, betting

app = FastAPI(title="競馬AI API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# USE_JRAVAN=1 を環境変数に設定すると PostgreSQL DataSource を使用する
if os.getenv("USE_JRAVAN", "0") == "1":
    ds = JRAVANDataSource()
else:
    ds = MockDataSource()

app.include_router(races.get_router(ds),      prefix="/api/races", tags=["races"])
app.include_router(prediction.get_router(ds), prefix="/api/races", tags=["prediction"])
app.include_router(betting.get_router(ds),    prefix="/api/races", tags=["betting"])
