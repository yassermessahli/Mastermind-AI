import type { HistoryEntry } from '../api/client'
import { idxToColorArray } from '../api/utils'
import { PegDisplay } from './PegDisplay'

interface GameBoardProps {
  history: HistoryEntry[]
  n_pegs: number
  n_colors: number
  max_steps: number
}

function FeedbackDots({ blacks, whites, n_pegs }: { blacks: number; whites: number; n_pegs: number }) {
  const dots = []
  for (let i = 0; i < n_pegs; i++) {
    if (i < blacks) {
      dots.push(
        <div key={i} style={{ width: 12, height: 12, borderRadius: '50%', backgroundColor: '#000' }} />,
      )
    } else if (i < blacks + whites) {
      dots.push(
        <div key={i} style={{ width: 12, height: 12, borderRadius: '50%', backgroundColor: 'transparent', border: '2px solid #fff' }} />,
      )
    } else {
      dots.push(
        <div key={i} style={{ width: 12, height: 12, borderRadius: '50%', backgroundColor: 'transparent', border: '2px solid #4b5563' }} />,
      )
    }
  }
  return <div className="flex flex-wrap gap-1" style={{ width: 32 }}>{dots}</div>
}

export function GameBoard({ history, n_pegs, n_colors, max_steps }: GameBoardProps) {
  const rows = []

  for (let i = 0; i < max_steps; i++) {
    const entry = history[i]
    const colors = entry ? idxToColorArray(entry[0], n_colors, n_pegs) : null

    rows.push(
      <div
        key={i}
        className="flex items-center gap-3 px-4 py-2 rounded-lg"
        style={{
          backgroundColor: entry ? 'rgba(255,255,255,0.05)' : 'rgba(255,255,255,0.02)',
          border: '1px solid rgba(255,255,255,0.08)',
        }}
      >
        <span className="text-gray-500 w-5 text-sm text-right">{i + 1}</span>
        <div className="flex gap-2">
          {Array.from({ length: n_pegs }).map((_, j) => (
            <PegDisplay key={j} color={colors ? colors[j] : null} size={28} />
          ))}
        </div>
        <div className="ml-auto">
          {entry ? (
            <FeedbackDots blacks={entry[1]} whites={entry[2]} n_pegs={n_pegs} />
          ) : (
            <div style={{ width: 32 }} />
          )}
        </div>
      </div>,
    )
  }

  return <div className="flex flex-col gap-1 w-full">{rows}</div>
}
