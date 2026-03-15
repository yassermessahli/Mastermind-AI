import { useState, useCallback } from 'react'
import {
  gameApi,
  type GameMode,
  type HistoryEntry,
} from '../api/client'

interface GameState {
  mode: GameMode | null
  n_colors: number
  n_pegs: number
  max_steps: number
  step: number
  terminated: boolean
  truncated: boolean
  history: HistoryEntry[]
  ai_guess: number[] | null
  ai_guess_idx: number | null
  started: boolean
}

const initialState: GameState = {
  mode: null,
  n_colors: 5,
  n_pegs: 4,
  max_steps: 8,
  step: 0,
  terminated: false,
  truncated: false,
  history: [],
  ai_guess: null,
  ai_guess_idx: null,
  started: false,
}

export function useGameState() {
  const [state, setState] = useState<GameState>(initialState)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const startGame = useCallback(
    async (mode: GameMode, n_colors: number, n_pegs: number, max_steps: number) => {
      setLoading(true)
      setError(null)
      try {
        const res = await gameApi.start({ mode, n_colors, n_pegs, max_steps })
        setState({
          mode: res.mode,
          n_colors: res.n_colors,
          n_pegs: res.n_pegs,
          max_steps: res.max_steps,
          step: res.step,
          terminated: res.terminated,
          truncated: res.truncated,
          history: res.history ?? [],
          ai_guess: res.ai_guess ?? null,
          ai_guess_idx: res.ai_guess_idx ?? null,
          started: true,
        })
      } catch (e) {
        setError('Failed to start game. Is the backend running?')
        console.error(e)
      } finally {
        setLoading(false)
      }
    },
    [],
  )

  const submitGuess = useCallback(async (guess_idx: number) => {
    setLoading(true)
    setError(null)
    try {
      const res = await gameApi.guess({ guess_idx })
      setState((prev) => ({
        ...prev,
        step: res.step,
        terminated: res.terminated,
        truncated: res.truncated,
        history: res.history,
      }))
    } catch (e) {
      setError('Failed to submit guess.')
      console.error(e)
    } finally {
      setLoading(false)
    }
  }, [])

  const submitFeedback = useCallback(async (blacks: number, whites: number) => {
    setLoading(true)
    setError(null)
    try {
      const res = await gameApi.feedback({ blacks, whites })
      setState((prev) => ({
        ...prev,
        step: res.step,
        terminated: res.terminated,
        truncated: res.truncated,
        history: res.history,
        ai_guess: res.ai_guess ?? null,
        ai_guess_idx: res.ai_guess_idx ?? null,
      }))
    } catch (e) {
      setError('Failed to submit feedback.')
      console.error(e)
    } finally {
      setLoading(false)
    }
  }, [])

  const resetGame = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      await gameApi.reset()
      setState(initialState)
    } catch (e) {
      setError('Failed to reset game.')
      console.error(e)
    } finally {
      setLoading(false)
    }
  }, [])

  return { state, loading, error, startGame, submitGuess, submitFeedback, resetGame }
}
