import type { GameMode } from '../api/client'
import { Info } from 'lucide-react'

interface SettingsPanelProps {
  mode: GameMode
  n_colors: number
  n_pegs: number
  max_steps: number
  onChange: (key: 'n_colors' | 'n_pegs' | 'max_steps', value: number) => void
}

interface StepperProps {
  label: string
  value: number
  min: number
  max: number
  onChange: (v: number) => void
  disabled?: boolean
}

function Stepper({ label, value, min, max, onChange, disabled }: StepperProps) {
  return (
    <div className="flex flex-col gap-2">
      <label className="text-gray-300 text-sm font-medium">{label}</label>
      <div className="flex items-center gap-3">
        <button
          onClick={() => onChange(Math.max(min, value - 1))}
          disabled={disabled || value <= min}
          className="w-8 h-8 rounded-full text-base font-bold"
          style={{
            backgroundColor: '#374151',
            color: value <= min ? '#4b5563' : '#fff',
            border: 'none',
            cursor: value <= min || disabled ? 'not-allowed' : 'pointer',
          }}
        >
          -
        </button>
        <span className="text-white font-bold text-lg w-6 text-center">{value}</span>
        <button
          onClick={() => onChange(Math.min(max, value + 1))}
          disabled={disabled || value >= max}
          className="w-8 h-8 rounded-full text-base font-bold"
          style={{
            backgroundColor: '#374151',
            color: value >= max ? '#4b5563' : '#fff',
            border: 'none',
            cursor: value >= max || disabled ? 'not-allowed' : 'pointer',
          }}
        >
          +
        </button>
        <span className="text-gray-500 text-xs ml-1">({min}–{max})</span>
      </div>
    </div>
  )
}

export function SettingsPanel({ mode, n_colors, n_pegs, max_steps, onChange }: SettingsPanelProps) {
  const locked = mode === 'codekeeper'

  return (
    <div className="flex flex-col gap-5">
      {locked && (
        <div
          className="flex items-start gap-2 p-3 rounded-lg text-sm"
          style={{
            backgroundColor: 'rgba(251,191,36,0.1)',
            border: '1px solid rgba(251,191,36,0.3)',
            color: '#fbbf24',
          }}
        >
          <Info size={16} className="mt-0.5 shrink-0" />
          <span>
            Codekeeper mode uses the default trained model configuration (5 colors, 4 pegs, 8 guesses) and cannot be changed.
          </span>
        </div>
      )}
      <Stepper
        label="Number of colors"
        value={n_colors}
        min={3}
        max={6}
        onChange={(v) => onChange('n_colors', v)}
        disabled={locked}
      />
      <Stepper
        label="Number of pegs"
        value={n_pegs}
        min={3}
        max={6}
        onChange={(v) => onChange('n_pegs', v)}
        disabled={locked}
      />
      <Stepper
        label="Guess limit"
        value={max_steps}
        min={5}
        max={10}
        onChange={(v) => onChange('max_steps', v)}
        disabled={locked}
      />
    </div>
  )
}
