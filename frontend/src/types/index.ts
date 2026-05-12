export interface HorseEntry {
  umaban: number;
  frame: number;
  horse_name: string;
  jockey: string;
  trainer: string;
  age: string;
  weight: number;
  odds: number;
  recent_form: string;
}

export interface RaceSummary {
  race_id: string;
  race_name: string;
  date: string;
  place: string;
  course_type: string;
  distance: number;
}

export interface Race extends RaceSummary {
  weather: string;
  track_condition: string;
  entries: HorseEntry[];
}

export interface PredictionEntry {
  umaban: number;
  horse_name: string;
  score: number;
  rank: number;
  win_probability: number;
}

export interface PredictionResult {
  race_id: string;
  predictions: PredictionEntry[];
}

export interface BettingTicket {
  bet_type: string;
  combination: number[];
  score: number;
}

export interface BettingResult {
  race_id: string;
  tansho: BettingTicket[];
  umatan: BettingTicket[];
  sanrentan: BettingTicket[];
}
