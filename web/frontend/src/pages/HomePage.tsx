import { useNavigate } from 'react-router-dom'
import { Shield, Search } from 'lucide-react'
import type { GameMode } from '../api/client'

export function HomePage() {
  const navigate = useNavigate()

  function go(mode: GameMode) {
    navigate(`/settings/${mode}`)
  }

  return (
    <div
      className="min-h-screen flex flex-col items-center justify-center p-6"
      style={{ backgroundColor: '#111827' }}
    >
      <h1 className="text-4xl font-bold text-white mb-2 text-center">Mastermind</h1>
      <p className="text-gray-400 mb-12 text-center text-lg">Choose your game mode</p>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-6 w-full max-w-2xl">
        <button
          onClick={() => go('codebreaker')}
          className="flex flex-col items-start gap-4 p-6 rounded-2xl text-left transition-transform hover:scale-105 focus:outline-none focus:ring-2 focus:ring-indigo-400"
          style={{
            backgroundColor: '#1f2937',
            border: '1px solid rgba(99,102,241,0.4)',
            cursor: 'pointer',
          }}
        >
          <div
            className="p-3 rounded-xl"
            style={{ backgroundColor: 'rgba(99,102,241,0.15)' }}
          >
            <Search size={28} className="text-indigo-400" />
          </div>
          <div>
            <h2 className="text-xl font-bold text-white mb-1">Codebreaker</h2>
            <p className="text-gray-400 text-sm">
              Try to guess the secret color code. You get black pegs for correct color and position, white pegs for correct color in the wrong position.
            </p>
          </div>
        </button>

        <button
          onClick={() => go('codekeeper')}
          className="flex flex-col items-start gap-4 p-6 rounded-2xl text-left transition-transform hover:scale-105 focus:outline-none focus:ring-2 focus:ring-purple-400"
          style={{
            backgroundColor: '#1f2937',
            border: '1px solid rgba(168,85,247,0.4)',
            cursor: 'pointer',
          }}
        >
          <div
            className="p-3 rounded-xl"
            style={{ backgroundColor: 'rgba(168,85,247,0.15)' }}
          >
            <Shield size={28} className="text-purple-400" />
          </div>
          <div>
            <h2 className="text-xl font-bold text-white mb-1">Codekeeper</h2>
            <p className="text-gray-400 text-sm">
              You hold the secret code in your head. The AI agent tries to guess it. Give honest feedback after each AI guess.
            </p>
          </div>
        </button>
      </div>
    </div>
  )
}
