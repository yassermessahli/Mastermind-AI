import { useState } from 'react'
import type { GameMode } from '../api/client'

export interface GameSettings {
  mode: GameMode
  n_colors: number
  n_pegs: number
  max_steps: number
}

const DEFAULTS: Omit<GameSettings, 'mode'> = {
  n_colors: 5,
  n_pegs: 4,
  max_steps: 8,
}

export function useSettings(mode: GameMode) {
  const isCodekeeper = mode === 'codekeeper'

  const [settings, setSettings] = useState<GameSettings>({
    mode,
    ...DEFAULTS,
  })

  function set(key: keyof Omit<GameSettings, 'mode'>, value: number) {
    if (isCodekeeper) return
    setSettings((prev) => ({ ...prev, [key]: value }))
  }

  return { settings, set, isCodekeeper }
}
