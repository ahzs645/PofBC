// Which years along a row of bars get a label, from the row's measured width (parts.jsx).

/** A year's label at 10px ("23/24", the widest), and the least space between two. */
const LABEL_WIDTH = 28
const LABEL_GAP = 4

/**
 * Which of `count` columns across `width` pixels carry a year label: every so many, as many as fit,
 * and `chosen` always. A label that centred under its column would run past either end of the chart
 * is set against that end instead, and any label that would then touch one already placed (the
 * chosen one first) is left out. Before the width is known every label is shown, centred.
 */
export const labelPlan = (count, width, chosen = -1, gap = 0) => {
  if (!width) return Array.from({ length: count }, () => ({ shown: true }))
  const column = (width - gap * (count - 1)) / count
  const stride = Math.max(1, Math.ceil((LABEL_WIDTH + LABEL_GAP) / Math.max(column + gap, 1)))
  const plan = Array.from({ length: count }, (_, at) => {
    const start = at * (column + gap)
    const centre = start + column / 2
    const edge = centre < LABEL_WIDTH / 2 ? 'start' : width - centre < LABEL_WIDTH / 2 ? 'end' : undefined
    const left = edge === 'start' ? start : edge === 'end' ? start + column - LABEL_WIDTH : centre - LABEL_WIDTH / 2
    return { shown: false, edge, left }
  })
  const placed = []
  const place = (at) => {
    const { left } = plan[at]
    if (placed.some((other) => Math.abs(other - left) < LABEL_WIDTH + LABEL_GAP)) return
    placed.push(left)
    plan[at].shown = true
  }
  if (chosen >= 0 && chosen < count) place(chosen)
  for (let at = 0; at < count; at += stride) place(at)
  return plan.map(({ shown, edge }) => ({ shown, edge }))
}
