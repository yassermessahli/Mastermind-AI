import { PegDisplay } from './PegDisplay'
import { Brain } from 'lucide-react'

interface AiGuessDisplayProps {
  guess: number[] | null
  step: number
}

export function AiGuessDisplay({ guess, step }: AiGuessDisplayProps) {
  return (
    <div
      className="flex flex-col items-center gap-3 p-5 rounded-xl"
      style={{
        backgroundColor: 'rgba(99,102,241,0.1)',
        border: '1px solid rgba(99,102,241,0.3)',
      }}
    >
      <div className="flex items-center gap-2">
        <Brain size={18} className="text-indigo-400" />
        <span className="text-indigo-300 font-semibold text-sm">AI Guess #{step}</span>
      </div>
      {guess ? (
        <div className="flex gap-3">
          {guess.map((color, i) => (
            <PegDisplay key={i} color={color} size={36} />
          ))}
        </div>
      ) : (
        <p className="text-gray-500 text-sm">Waiting for feedback…</p>
      )}
    </div>
  )
}
