import { useEffect } from 'react'
import { useNavigate, useLocation } from 'react-router-dom'
import { ArrowLeft } from 'lucide-react'
import { useGameState } from '../hooks/useGameState'
import { GameBoard } from '../components/GameBoard'
import { FeedbackInput } from '../components/FeedbackInput'
import { AiGuessDisplay } from '../components/AiGuessDisplay'
import { ResultModal } from '../components/ResultModal'

interface LocationState {
  n_colors: number
  n_pegs: number
  max_steps: number
}

export function CodekeeperPage() {
  const navigate = useNavigate()
  const location = useLocation()
  const { state: gameState, loading, error, startGame, submitFeedback, resetGame } = useGameState()

  const settings = (location.state ?? {}) as Partial<LocationState>
  const max_steps = settings.max_steps ?? 8

  // eslint-disable-next-line react-hooks/exhaustive-deps
  useEffect(() => { startGame('codekeeper', 5, 4, 8) }, [])

  async function handleFeedback(blacks: number, whites: number) {
    await submitFeedback(blacks, whites)
  }

  async function handlePlayAgain() {
    await resetGame()
    navigate('/settings/codekeeper')
  }

  const isOver = gameState.terminated || gameState.truncated
  const won = gameState.terminated

  return (
    <div
      className="min-h-screen flex flex-col items-center p-4 sm:p-6"
      style={{ backgroundColor: '#111827' }}
    >
      <div className="w-full max-w-md">
        <div className="flex items-center justify-between mb-6">
          <button
            onClick={() => navigate('/settings/codekeeper')}
            className="flex items-center gap-2 text-gray-400 hover:text-white transition-colors"
            style={{ background: 'none', border: 'none', cursor: 'pointer', padding: 0 }}
          >
            <ArrowLeft size={16} />
            <span className="text-sm">Settings</span>
          </button>
          <h1 className="text-lg font-bold text-white">Codekeeper</h1>
          <span className="text-gray-500 text-sm">
            {gameState.step}/{max_steps}
          </span>
        </div>

        {error && (
          <div
            className="mb-4 p-3 rounded-lg text-sm text-red-300"
            style={{ backgroundColor: 'rgba(239,68,68,0.1)', border: '1px solid rgba(239,68,68,0.3)' }}
          >
            {error}
          </div>
        )}

        {gameState.started && (
          <>
            {!isOver && gameState.ai_guess && (
              <div className="mb-6">
                <AiGuessDisplay
                  guess={gameState.ai_guess}
                  step={gameState.step + 1}
                />
              </div>
            )}

            {!isOver && gameState.ai_guess && (
              <div
                className="p-5 rounded-2xl mb-6"
                style={{ backgroundColor: '#1f2937', border: '1px solid rgba(255,255,255,0.08)' }}
              >
                <FeedbackInput
                  n_pegs={gameState.n_pegs}
                  onSubmit={handleFeedback}
                  disabled={loading}
                />
              </div>
            )}

            {gameState.history.length > 0 && (
              <div>
                <p className="text-gray-500 text-xs mb-2 uppercase tracking-wider">AI Guess History</p>
                <GameBoard
                  history={gameState.history}
                  n_pegs={gameState.n_pegs}
                  n_colors={gameState.n_colors}
                  max_steps={gameState.max_steps}
                />
              </div>
            )}
          </>
        )}

        {!gameState.started && !error && (
          <div className="flex justify-center mt-20">
            <p className="text-gray-400">Starting game…</p>
          </div>
        )}
      </div>

      {isOver && (
        <ResultModal
          won={won}
          steps={gameState.step}
          max_steps={gameState.max_steps}
          onPlayAgain={handlePlayAgain}
        />
      )}
    </div>
  )
}
