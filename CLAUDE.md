# CLAUDE.md

このファイルは、リポジトリ内のコードを扱う際に Claude Code (claude.ai/code) へ提供するガイダンスです。

## 言語設定

すべての応答とコードコメントは日本語で記述してください。

## 起動コマンド

```powershell
# バックエンド（FastAPI / モックデータ）
cd backend
..\venv\Scripts\uvicorn main:app --reload

# バックエンド（PostgreSQL 実データ使用）
$env:USE_JRAVAN="1"; ..\venv\Scripts\uvicorn main:app --reload

# JV-Data 取り込み（初回全件: --option 2 / 差分更新: --option 1）
cd backend
$env:JVLINK_SID="YOUR_SID"   # JRA-VAN マイページで確認
..\venv\Scripts\python -m db.etl --from 20200101 --option 2

# フロントエンド（React + Vite）
cd frontend
npm install   # 初回のみ
npm run dev
# → http://localhost:5173

# 一括起動（ルートから）
.\start.ps1
```

## アーキテクチャ

競馬 AI Web アプリ。JRA-VAN データをもとに出馬表表示・AI予測・買い目自動生成を行う。  
現在は `backend/mock/data.py` のモックデータで動作する。JRA-VAN 接続時は `MockDataSource` を差し替える。

### バックエンド（`backend/`）

| ファイル | 役割 |
|---|---|
| `main.py` | FastAPI アプリ、CORS設定、ルーター登録 |
| `models/schemas.py` | Pydantic モデル（Race, HorseEntry, PredictionResult, BettingResult 等） |
| `mock/data.py` | モックレースデータ（JRA-VAN 接続まで使用） |
| `services/data_source.py` | `DataSource` 抽象クラスと `MockDataSource`。JRA-VAN 対応時はここを実装する |
| `services/predictor.py` | オッズ(65%) + 近走成績(35%) でスコアリングし勝率を算出 |
| `services/betting_service.py` | 上位4頭の順列から単勝・馬単・三連単の買い目を生成 |
| `routers/races.py` | `GET /api/races?date=` と `GET /api/races/{race_id}` |
| `routers/prediction.py` | `GET /api/races/{race_id}/prediction` |
| `routers/betting.py` | `GET /api/races/{race_id}/betting` |

### フロントエンド（`frontend/`）

| ファイル | 役割 |
|---|---|
| `src/api/client.ts` | fetch ラッパー（4つのAPIエンドポイントを呼び出す） |
| `src/types/index.ts` | バックエンドのスキーマに対応する TypeScript 型定義 |
| `src/pages/RaceList.tsx` | 日付選択 → レース一覧表示 |
| `src/pages/RaceDetail.tsx` | 出馬表 / 予測・スコア / 買い目 の3タブ表示 |

Vite の proxy 設定（`vite.config.ts`）で `/api` を `localhost:8000` に転送する。

### データの流れ

```
RaceList → GET /api/races?date= → MockDataSource.get_race_list()
RaceDetail → GET /api/races/{id}          → MockDataSource.get_race()
           → GET /api/races/{id}/prediction → Predictor.predict()
           → GET /api/races/{id}/betting   → BettingService.generate()
```

### race_id の形式

`YYYYMMDDPPNN`（仮形式、JRA-VAN 導入時に合わせて変更する）
- YYYY = 年、MM = 月、DD = 日、PP = 場コード（01=東京, 02=中山…）、NN = レース番号

### JRA-VAN 接続時の差し替え手順

1. `services/data_source.py` に `JRAVANDataSource(DataSource)` を実装する
2. `main.py` の `ds = MockDataSource()` を `ds = JRAVANDataSource()` に変更する
3. `mock/data.py` はそのまま残してテスト用に使える

## モックデータのデフォルト日付

`20260510`（東京11R・中山11R の2レースが登録されている）
