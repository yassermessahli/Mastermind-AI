import axios from 'axios'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL ?? 'http://localhost:8000',
  withCredentials: true,
})

export type GameMode = 'codebreaker' | 'codekeeper'

export type HistoryEntry = [number, number, number]

export interface StartRequest {
  mode: GameMode
  n_colors: number
  n_pegs: number
  max_steps: number
}

export interface StartResponse {
  mode: GameMode
  n_colors: number
  n_pegs: number
  max_steps: number
  step: number
  terminated: boolean
  truncated: boolean
  history: HistoryEntry[]
  ai_guess_idx?: number
  ai_guess?: number[]
  consistent_set_size?: number
}

export interface GuessRequest {
  guess_idx: number
}

export interface GuessResponse {
  blacks: number
  whites: number
  terminated: boolean
  truncated: boolean
  step: number
  history: HistoryEntry[]
}

export interface FeedbackRequest {
  blacks: number
  whites: number
}

export interface FeedbackResponse {
  terminated: boolean
  truncated: boolean
  step: number
  consistent_set_size: number
  history: HistoryEntry[]
  ai_guess_idx?: number
  ai_guess?: number[]
}

export interface GameStateResponse {
  mode: GameMode
  n_colors: number
  n_pegs: number
  max_steps: number
  step: number
  terminated: boolean
  truncated: boolean
  history: HistoryEntry[]
  ai_guess?: number[]
  ai_guess_idx?: number
  consistent_set_size?: number
}

export interface ResetResponse {
  ok: boolean
}

export const gameApi = {
  start: (data: StartRequest) =>
    api.post<StartResponse>('/api/game/start/', data).then((r) => r.data),

  guess: (data: GuessRequest) =>
    api.post<GuessResponse>('/api/game/guess/', data).then((r) => r.data),

  feedback: (data: FeedbackRequest) =>
    api.post<FeedbackResponse>('/api/game/feedback/', data).then((r) => r.data),

  state: () =>
    api.get<GameStateResponse>('/api/game/state/').then((r) => r.data),

  reset: () =>
    api.post<ResetResponse>('/api/game/reset/').then((r) => r.data),
}
