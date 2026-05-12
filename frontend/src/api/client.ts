import type { Race, RaceSummary, PredictionResult, BettingResult } from "../types";

const BASE = "/api/races";

async function get<T>(url: string): Promise<T> {
  const res = await fetch(url);
  if (!res.ok) throw new Error(`${res.status} ${res.statusText}`);
  return res.json() as Promise<T>;
}

export const api = {
  getRaces: (date: string) =>
    get<RaceSummary[]>(`${BASE}?date=${date}`),

  getRace: (raceId: string) =>
    get<Race>(`${BASE}/${raceId}`),

  getPrediction: (raceId: string) =>
    get<PredictionResult>(`${BASE}/${raceId}/prediction`),

  getBetting: (raceId: string) =>
    get<BettingResult>(`${BASE}/${raceId}/betting`),
};
