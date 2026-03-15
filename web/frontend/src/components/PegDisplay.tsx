const PEG_COLORS: Record<number, string> = {
  0: '#ef4444',
  1: '#3b82f6',
  2: '#22c55e',
  3: '#facc15',
  4: '#a855f7',
  5: '#f97316',
}

interface PegDisplayProps {
  color: number | null
  size?: number
}

export function PegDisplay({ color, size = 32 }: PegDisplayProps) {
  const bg = color !== null ? PEG_COLORS[color] : 'transparent'
  const border = color !== null ? PEG_COLORS[color] : '#6b7280'

  return (
    <div
      style={{
        width: size,
        height: size,
        borderRadius: '50%',
        backgroundColor: bg,
        border: `2px solid ${border}`,
        flexShrink: 0,
      }}
    />
  )
}

export { PEG_COLORS }
