import { useState } from 'react'
import { PegDisplay, PEG_COLORS } from './PegDisplay'

interface GuessInputProps {
  n_pegs: number
  n_colors: number
  onSubmit: (guess: number[]) => void
  disabled?: boolean
}

export function GuessInput({ n_pegs, n_colors, onSubmit, disabled }: GuessInputProps) {
  const [pegs, setPegs] = useState<(number | null)[]>(Array(n_pegs).fill(null))

  const allSelected = pegs.every((p) => p !== null)

  function cyclePeg(idx: number) {
    if (disabled) return
    setPegs((prev) => {
      const next = [...prev]
      const current = next[idx]
      next[idx] = current === null ? 0 : current + 1 >= n_colors ? null : current + 1
      return next
    })
  }

  function handleSubmit() {
    if (!allSelected || disabled) return
    onSubmit(pegs as number[])
    setPegs(Array(n_pegs).fill(null))
  }

  return (
    <div className="flex flex-col items-center gap-4">
      <p className="text-gray-400 text-sm">Click pegs to cycle colors, then submit your guess</p>
      <div className="flex gap-3 items-center">
        {pegs.map((color, i) => (
          <button
            key={i}
            onClick={() => cyclePeg(i)}
            disabled={disabled}
            className="cursor-pointer rounded-full transition-transform hover:scale-110 focus:outline-none focus:ring-2 focus:ring-white/40"
            style={{ padding: 0, background: 'none', border: 'none' }}
            aria-label={`Peg ${i + 1}: ${color !== null ? `color ${color}` : 'empty'}`}
          >
            <PegDisplay color={color} size={36} />
          </button>
        ))}
      </div>
      <div className="flex gap-2 flex-wrap justify-center">
        <p className="text-gray-500 text-xs w-full text-center">Colors available:</p>
        {Array.from({ length: n_colors }).map((_, c) => (
          <div key={c} className="flex items-center gap-1">
            <div
              style={{
                width: 14,
                height: 14,
                borderRadius: '50%',
                backgroundColor: PEG_COLORS[c],
              }}
            />
          </div>
        ))}
      </div>
      <button
        onClick={handleSubmit}
        disabled={!allSelected || disabled}
        className="px-6 py-2 rounded-lg font-semibold text-sm transition-colors"
        style={{
          backgroundColor: allSelected && !disabled ? '#6366f1' : '#374151',
          color: allSelected && !disabled ? '#fff' : '#6b7280',
          cursor: allSelected && !disabled ? 'pointer' : 'not-allowed',
        }}
      >
        Submit Guess
      </button>
    </div>
  )
}
