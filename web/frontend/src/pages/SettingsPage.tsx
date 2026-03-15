import { useNavigate, useParams } from 'react-router-dom'
import { ArrowLeft } from 'lucide-react'
import type { GameMode } from '../api/client'
import { useSettings } from '../hooks/useSettings'
import { SettingsPanel } from '../components/SettingsPanel'

export function SettingsPage() {
  const { mode } = useParams<{ mode: string }>()
  const navigate = useNavigate()
  const gameMode = (mode ?? 'codebreaker') as GameMode
  const { settings, set } = useSettings(gameMode)

  function handleStart() {
    const path = gameMode === 'codebreaker' ? '/play/codebreaker' : '/play/codekeeper'
    navigate(path, {
      state: {
        n_colors: settings.n_colors,
        n_pegs: settings.n_pegs,
        max_steps: settings.max_steps,
      },
    })
  }

  return (
    <div
      className="min-h-screen flex flex-col items-center justify-center p-6"
      style={{ backgroundColor: '#111827' }}
    >
      <div className="w-full max-w-sm">
        <button
          onClick={() => navigate('/')}
          className="flex items-center gap-2 text-gray-400 hover:text-white mb-8 transition-colors"
          style={{ background: 'none', border: 'none', cursor: 'pointer', padding: 0 }}
        >
          <ArrowLeft size={16} />
          <span className="text-sm">Back</span>
        </button>

        <h1 className="text-2xl font-bold text-white mb-1">
          {gameMode === 'codebreaker' ? 'Codebreaker' : 'Codekeeper'} Settings
        </h1>
        <p className="text-gray-400 text-sm mb-8">Configure the game parameters</p>

        <div
          className="p-6 rounded-2xl mb-6"
          style={{ backgroundColor: '#1f2937', border: '1px solid rgba(255,255,255,0.08)' }}
        >
          <SettingsPanel
            mode={gameMode}
            n_colors={settings.n_colors}
            n_pegs={settings.n_pegs}
            max_steps={settings.max_steps}
            onChange={set}
          />
        </div>

        <button
          onClick={handleStart}
          className="w-full py-3 rounded-xl font-semibold text-white transition-colors"
          style={{ backgroundColor: '#6366f1', border: 'none', cursor: 'pointer', fontSize: '1rem' }}
        >
          Start Game
        </button>
      </div>
    </div>
  )
}
