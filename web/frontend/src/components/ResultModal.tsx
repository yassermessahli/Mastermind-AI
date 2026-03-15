import { Trophy, Frown, RotateCcw } from 'lucide-react'

interface ResultModalProps {
  won: boolean
  steps: number
  max_steps: number
  onPlayAgain: () => void
}

export function ResultModal({ won, steps, max_steps, onPlayAgain }: ResultModalProps) {
  return (
    <div
      className="fixed inset-0 flex items-center justify-center z-50"
      style={{ backgroundColor: 'rgba(0,0,0,0.75)' }}
    >
      <div
        className="flex flex-col items-center gap-5 p-8 rounded-2xl text-center max-w-sm w-full mx-4"
        style={{
          backgroundColor: '#1f2937',
          border: '1px solid rgba(255,255,255,0.1)',
        }}
      >
        {won ? (
          <>
            <Trophy size={48} className="text-yellow-400" />
            <h2 className="text-2xl font-bold text-white">You Win!</h2>
            <p className="text-gray-400">
              Solved in <span className="text-white font-semibold">{steps}</span> of {max_steps} guesses
            </p>
          </>
        ) : (
          <>
            <Frown size={48} className="text-gray-400" />
            <h2 className="text-2xl font-bold text-white">Game Over</h2>
            <p className="text-gray-400">
              Used all {max_steps} guesses without solving the code.
            </p>
          </>
        )}

        <button
          onClick={onPlayAgain}
          className="flex items-center gap-2 px-6 py-2 rounded-lg font-semibold text-sm mt-2"
          style={{
            backgroundColor: '#6366f1',
            color: '#fff',
            border: 'none',
            cursor: 'pointer',
          }}
        >
          <RotateCcw size={16} />
          Play Again
        </button>
      </div>
    </div>
  )
}
