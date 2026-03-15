import { useEffect } from 'react'
import { useNavigate, useLocation } from 'react-router-dom'
import { ArrowLeft } from 'lucide-react'
import { useGameState } from '../hooks/useGameState'
import { GameBoard } from '../components/GameBoard'
import { GuessInput } from '../components/GuessInput'
import { ResultModal } from '../components/ResultModal'
import { colorArrayToIdx } from '../api/utils'

interface LocationState {
  n_colors: number
  n_pegs: number
  max_steps: number
}

export function CodebreakerPage() {
  const navigate = useNavigate()
  const location = useLocation()
  const { state: gameState, loading, error, startGame, submitGuess, resetGame } = useGameState()

  const settings = (location.state ?? {}) as Partial<LocationState>
  const n_colors = settings.n_colors ?? 5
  const n_pegs = settings.n_pegs ?? 4
  const max_steps = settings.max_steps ?? 8

  // eslint-disable-next-line react-hooks/exhaustive-deps
  useEffect(() => { startGame('codebreaker', n_colors, n_pegs, max_steps) }, [])

  async function handleGuess(colors: number[]) {
    const idx = colorArrayToIdx(colors, n_colors)
    await submitGuess(idx)
  }

  async function handlePlayAgain() {
    await resetGame()
    navigate('/settings/codebreaker')
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
            onClick={() => navigate('/settings/codebreaker')}
            className="flex items-center gap-2 text-gray-400 hover:text-white transition-colors"
            style={{ background: 'none', border: 'none', cursor: 'pointer', padding: 0 }}
          >
            <ArrowLeft size={16} />
            <span className="text-sm">Settings</span>
          </button>
          <h1 className="text-lg font-bold text-white">Codebreaker</h1>
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
            <div className="mb-6">
              <GameBoard
                history={gameState.history}
                n_pegs={gameState.n_pegs}
                n_colors={gameState.n_colors}
                max_steps={gameState.max_steps}
              />
            </div>

            {!isOver && (
              <div
                className="p-5 rounded-2xl"
                style={{ backgroundColor: '#1f2937', border: '1px solid rgba(255,255,255,0.08)' }}
              >
                <GuessInput
                  n_pegs={gameState.n_pegs}
                  n_colors={gameState.n_colors}
                  onSubmit={handleGuess}
                  disabled={loading || isOver}
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
