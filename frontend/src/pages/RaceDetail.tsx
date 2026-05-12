import { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { api } from "../api/client";
import type { Race, PredictionResult, BettingResult } from "../types";

type Tab = "shutuba" | "prediction" | "betting";

function RankBadge({ rank }: { rank: number }) {
  const cls =
    rank === 1 ? "rank-badge rank-1"
    : rank === 2 ? "rank-badge rank-2"
    : rank === 3 ? "rank-badge rank-3"
    : "rank-badge rank-other";
  return <span className={cls}>{rank}</span>;
}

function ProbBar({ value }: { value: number }) {
  return (
    <div className="prob-bar-wrap">
      <div className="prob-bar-bg">
        <div className="prob-bar-fill" style={{ width: `${(value * 100).toFixed(1)}%` }} />
      </div>
      <span style={{ fontSize: ".8rem", width: 42, textAlign: "right" }}>
        {(value * 100).toFixed(1)}%
      </span>
    </div>
  );
}

function comboLabel(combination: number[]): string {
  return combination.join(" → ");
}

export default function RaceDetail() {
  const { raceId } = useParams<{ raceId: string }>();
  const navigate = useNavigate();

  const [tab, setTab] = useState<Tab>("shutuba");
  const [race, setRace] = useState<Race | null>(null);
  const [prediction, setPrediction] = useState<PredictionResult | null>(null);
  const [betting, setBetting] = useState<BettingResult | null>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!raceId) return;
    Promise.all([
      api.getRace(raceId),
      api.getPrediction(raceId),
      api.getBetting(raceId),
    ])
      .then(([r, p, b]) => {
        setRace(r);
        setPrediction(p);
        setBetting(b);
      })
      .catch(() => setError("データの取得に失敗しました。"));
  }, [raceId]);

  if (error) return <p className="error" style={{ margin: 24 }}>{error}</p>;
  if (!race) return <p className="loading">読み込み中…</p>;

  return (
    <>
      <header className="header">
        <button
          className="btn btn-outline"
          style={{ color: "#fff", borderColor: "#fff", padding: "6px 14px" }}
          onClick={() => navigate(-1)}
        >
          ← 戻る
        </button>
        <h1>🐎 競馬AI</h1>
      </header>

      <div className="container">
        {/* レース情報 */}
        <div className="race-header">
          <h2>{race.race_name}</h2>
          <div className="race-header-meta">
            <span className="meta-chip">{race.place}</span>
            <span className="meta-chip">{race.course_type} {race.distance}m</span>
            <span className="meta-chip">天候: {race.weather}</span>
            <span className="meta-chip">馬場: {race.track_condition}</span>
          </div>
        </div>

        {/* タブ */}
        <div className="tabs">
          {(["shutuba", "prediction", "betting"] as Tab[]).map((t) => {
            const label = t === "shutuba" ? "出馬表" : t === "prediction" ? "予測・スコア" : "買い目";
            return (
              <div
                key={t}
                className={`tab${tab === t ? " active" : ""}`}
                onClick={() => setTab(t)}
              >
                {label}
              </div>
            );
          })}
        </div>

        {/* 出馬表 */}
        {tab === "shutuba" && (
          <div className="card">
            <div className="table-wrap">
              <table>
                <thead>
                  <tr>
                    <th>枠</th><th>馬番</th><th>馬名</th><th>騎手</th>
                    <th>調教師</th><th>馬齢</th><th>斤量</th><th>オッズ</th><th>近走</th>
                  </tr>
                </thead>
                <tbody>
                  {race.entries.map((h) => (
                    <tr key={h.umaban}>
                      <td>{h.frame}</td>
                      <td>{h.umaban}</td>
                      <td style={{ fontWeight: 600 }}>{h.horse_name}</td>
                      <td>{h.jockey}</td>
                      <td>{h.trainer}</td>
                      <td>{h.age}</td>
                      <td>{h.weight}</td>
                      <td style={{ color: "#e8a020", fontWeight: 700 }}>{h.odds}</td>
                      <td style={{ fontFamily: "monospace" }}>{h.recent_form}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* 予測 */}
        {tab === "prediction" && prediction && (
          <div className="card">
            <div className="table-wrap">
              <table>
                <thead>
                  <tr>
                    <th>順位</th><th>馬番</th><th>馬名</th><th>スコア</th><th>勝利確率</th>
                  </tr>
                </thead>
                <tbody>
                  {prediction.predictions.map((p) => (
                    <tr key={p.umaban}>
                      <td><RankBadge rank={p.rank} /></td>
                      <td>{p.umaban}</td>
                      <td style={{ fontWeight: 600 }}>{p.horse_name}</td>
                      <td>{p.score.toFixed(4)}</td>
                      <td style={{ minWidth: 160 }}><ProbBar value={p.win_probability} /></td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* 買い目 */}
        {tab === "betting" && betting && (
          <div className="card">
            <div className="betting-section">
              <h3>単勝</h3>
              <div className="ticket-list">
                {betting.tansho.map((t, i) => (
                  <div key={i} className="ticket">
                    <span className="ticket-combo">{comboLabel(t.combination)}</span>
                    <span className="ticket-score">スコア: {(t.score * 100).toFixed(2)}%</span>
                  </div>
                ))}
              </div>
            </div>

            <div className="betting-section">
              <h3>馬単</h3>
              <div className="ticket-list">
                {betting.umatan.map((t, i) => (
                  <div key={i} className="ticket">
                    <span className="ticket-combo">{comboLabel(t.combination)}</span>
                    <span className="ticket-score">スコア: {(t.score * 10000).toFixed(2)}</span>
                  </div>
                ))}
              </div>
            </div>

            <div className="betting-section">
              <h3>三連単</h3>
              <div className="ticket-list">
                {betting.sanrentan.map((t, i) => (
                  <div key={i} className="ticket">
                    <span className="ticket-combo">{comboLabel(t.combination)}</span>
                    <span className="ticket-score">スコア: {(t.score * 1000000).toFixed(2)}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}
      </div>
    </>
  );
}
