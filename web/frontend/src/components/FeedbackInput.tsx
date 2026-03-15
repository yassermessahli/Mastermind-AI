import { useState } from 'react'

interface FeedbackInputProps {
  n_pegs: number
  onSubmit: (blacks: number, whites: number) => void
  disabled?: boolean
}

export function FeedbackInput({ n_pegs, onSubmit, disabled }: FeedbackInputProps) {
  const [blacks, setBlacks] = useState(0)
  const [whites, setWhites] = useState(0)

  const valid = blacks + whites <= n_pegs

  function clamp(v: number) {
    return Math.max(0, Math.min(n_pegs, v))
  }

  function handleSubmit() {
    if (!valid || disabled) return
    onSubmit(blacks, whites)
    setBlacks(0)
    setWhites(0)
  }

  return (
    <div className="flex flex-col items-center gap-4">
      <p className="text-gray-400 text-sm">Enter the feedback for the AI's guess</p>
      <div className="flex gap-8">
        <div className="flex flex-col items-center gap-2">
          <span className="text-sm font-semibold text-gray-300">Black pegs</span>
          <span className="text-xs text-gray-500">Correct color + position</span>
          <div className="flex items-center gap-2">
            <button
              onClick={() => setBlacks(clamp(blacks - 1))}
              disabled={disabled || blacks === 0}
              className="w-8 h-8 rounded-full text-lg font-bold transition-colors"
              style={{
                backgroundColor: '#374151',
                color: blacks === 0 ? '#4b5563' : '#fff',
                border: 'none',
                cursor: blacks === 0 || disabled ? 'not-allowed' : 'pointer',
              }}
            >
              -
            </button>
            <span className="text-white text-xl font-bold w-6 text-center">{blacks}</span>
            <button
              onClick={() => setBlacks(clamp(blacks + 1))}
              disabled={disabled || blacks + whites >= n_pegs}
              className="w-8 h-8 rounded-full text-lg font-bold transition-colors"
              style={{
                backgroundColor: '#374151',
                color: blacks + whites >= n_pegs ? '#4b5563' : '#fff',
                border: 'none',
                cursor: blacks + whites >= n_pegs || disabled ? 'not-allowed' : 'pointer',
              }}
            >
              +
            </button>
          </div>
        </div>

        <div className="flex flex-col items-center gap-2">
          <span className="text-sm font-semibold text-gray-300">White pegs</span>
          <span className="text-xs text-gray-500">Correct color, wrong position</span>
          <div className="flex items-center gap-2">
            <button
              onClick={() => setWhites(clamp(whites - 1))}
              disabled={disabled || whites === 0}
              className="w-8 h-8 rounded-full text-lg font-bold transition-colors"
              style={{
                backgroundColor: '#374151',
                color: whites === 0 ? '#4b5563' : '#fff',
                border: 'none',
                cursor: whites === 0 || disabled ? 'not-allowed' : 'pointer',
              }}
            >
              -
            </button>
            <span className="text-white text-xl font-bold w-6 text-center">{whites}</span>
            <button
              onClick={() => setWhites(clamp(whites + 1))}
              disabled={disabled || blacks + whites >= n_pegs}
              className="w-8 h-8 rounded-full text-lg font-bold transition-colors"
              style={{
                backgroundColor: '#374151',
                color: blacks + whites >= n_pegs ? '#4b5563' : '#fff',
                border: 'none',
                cursor: blacks + whites >= n_pegs || disabled ? 'not-allowed' : 'pointer',
              }}
            >
              +
            </button>
          </div>
        </div>
      </div>

      {!valid && (
        <p className="text-red-400 text-sm">Blacks + whites cannot exceed {n_pegs}</p>
      )}

      <button
        onClick={handleSubmit}
        disabled={!valid || disabled}
        className="px-6 py-2 rounded-lg font-semibold text-sm transition-colors"
        style={{
          backgroundColor: valid && !disabled ? '#6366f1' : '#374151',
          color: valid && !disabled ? '#fff' : '#6b7280',
          cursor: valid && !disabled ? 'pointer' : 'not-allowed',
          border: 'none',
        }}
      >
        Submit Feedback
      </button>
    </div>
  )
}
