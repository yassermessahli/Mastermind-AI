export function colorArrayToIdx(colors: number[], n_colors: number): number {
  let idx = 0
  for (let i = 0; i < colors.length; i++) {
    idx = idx * n_colors + colors[i]
  }
  return idx
}

export function idxToColorArray(idx: number, n_colors: number, n_pegs: number): number[] {
  const result = new Array(n_pegs)
  for (let i = n_pegs - 1; i >= 0; i--) {
    result[i] = idx % n_colors
    idx = Math.floor(idx / n_colors)
  }
  return result
}
