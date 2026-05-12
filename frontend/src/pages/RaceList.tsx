import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { api } from "../api/client";
import type { RaceSummary } from "../types";

function today(): string {
  return new Date().toISOString().slice(0, 10);
}

function toApiDate(dateInput: string): string {
  return dateInput.replace(/-/g, "");
}

function courseLabel(type: string, distance: number): string {
  return `${type} ${distance}m`;
}

export default function RaceList() {
  const [date, setDate] = useState(today());
  const [races, setRaces] = useState<RaceSummary[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [searched, setSearched] = useState(false);
  const navigate = useNavigate();

  const search = async () => {
    setLoading(true);
    setError("");
    setSearched(true);
    try {
      const data = await api.getRaces(toApiDate(date));
      setRaces(data);
    } catch {
      setError("データの取得に失敗しました。バックエンドが起動しているか確認してください。");
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      <header className="header">
        <h1>🐎 競馬AI</h1>
      </header>

      <div className="container">
        <div className="card">
          <div className="search-row">
            <input
              type="date"
              value={date}
              onChange={(e) => setDate(e.target.value)}
            />
            <button className="btn btn-primary" onClick={search} disabled={loading}>
              {loading ? "取得中…" : "レースを検索"}
            </button>
          </div>
        </div>

        {error && <p className="error">{error}</p>}

        {loading && <p className="loading">読み込み中…</p>}

        {!loading && searched && races.length === 0 && !error && (
          <p className="empty">この日のレースデータが見つかりませんでした。</p>
        )}

        {races.map((race) => (
          <div
            key={race.race_id}
            className="race-card"
            onClick={() => navigate(`/races/${race.race_id}`)}
          >
            <div>
              <div className="race-card-name">{race.race_name}</div>
              <div className="race-card-meta">
                {race.place}　{courseLabel(race.course_type, race.distance)}
              </div>
            </div>
            <span className="race-badge">{race.place}</span>
          </div>
        ))}
      </div>
    </>
  );
}
