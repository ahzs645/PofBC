// The Budget mode's arithmetic and geometry, kept apart from React so it can be tested.
//
// The flow is drawn through one middle bar, the consolidated total. The Province does not say which
// revenue pays for which function, so no source is ever joined straight to a function: each source
// flows into the total, and the total flows out to each function. When expense is larger, the
// difference enters as its own band ("Expense over revenue"); when revenue is larger, it leaves as
// one ("Revenue over expense").

import { BUDGET_STATEMENTS } from './budgetData.js'

// A fixed order, so a line keeps its place and colour from year to year. Functions take the
// categorical slots in this order (stacked neighbours are neighbouring slots, the order the palette
// was checked in); "Other" is the Province's own catch-all, drawn grey.
export const SOURCE_ORDER = ['taxation', 'federal', 'fees', 'resources', 'crowns', 'investment', 'miscellaneous', 'recoveries']
export const FUNCTION_ORDER = ['health', 'education', 'social', 'protection', 'transportation', 'development', 'general', 'interest', 'other']
export const BALANCE = 'balance'

export const BUDGET_YEARS = BUDGET_STATEMENTS.map((statement) => statement.year)
export const LATEST_YEAR = BUDGET_YEARS.at(-1)
export const statementFor = (year) => BUDGET_STATEMENTS.find((statement) => statement.year === year) ?? null

/** A fiscal year from the address bar, or the latest. */
export const readBudgetYear = (search = '') => {
  const value = new URLSearchParams(search).get('fy')
  return BUDGET_YEARS.includes(value) ? value : LATEST_YEAR
}

const millions = new Intl.NumberFormat('en-CA', { maximumFractionDigits: 0 })
/** "$49,446 million"; a deficit as "−$7,347 million". */
export const formatMillions = (value) => (value === null || value === undefined ? '—' : `${value < 0 ? '−' : ''}$${millions.format(Math.abs(value))} million`)
/** "49,446" for a table already headed "$ millions". */
export const formatFigure = (value) => (value === null || value === undefined ? '—' : `${value < 0 ? '−' : ''}${millions.format(Math.abs(value))}`)
/** "$84.0 billion", for the headline and the trend's axis. */
export const formatBillions = (value, digits = 1) => `${value < 0 ? '−' : ''}$${(Math.abs(value) / 1000).toFixed(digits)} billion`
export const formatShare = (part, whole) => (whole ? `${((part / whole) * 100).toFixed(1)}%` : '—')

const inOrder = (lines, order) => [...lines].sort((a, b) => order.indexOf(a.key) - order.indexOf(b.key))

/** The year's two columns of the flow, in the fixed order, with the balancing band where needed. */
export const flowColumns = (statement) => {
  const revenue = statement.revenue.total.actual
  const expense = statement.expense.total.actual
  const sources = inOrder(statement.revenue.lines, SOURCE_ORDER).map((line) => ({ ...line, side: 'source' }))
  const uses = inOrder(statement.expense.lines, FUNCTION_ORDER).map((line) => ({ ...line, side: 'function' }))
  const gap = expense - revenue
  if (gap > 0) sources.push({ key: BALANCE, heading: 'Expense over revenue', actual: gap, side: 'source' })
  if (gap < 0) uses.push({ key: BALANCE, heading: 'Revenue over expense', actual: -gap, side: 'function' })
  return { sources, uses, total: Math.max(revenue, expense), revenue, expense }
}

/** Words into lines of at most `width` characters; a longer word stands alone. */
export const wrap = (text, width) => {
  const lines = []
  for (const word of String(text).split(/\s+/)) {
    const last = lines.at(-1)
    if (last && `${last} ${word}`.length <= width) lines[lines.length - 1] = `${last} ${word}`
    else lines.push(word)
  }
  return lines
}

/** A ribbon of constant thickness from (x0, y0) to (x1, y1), its top edges at those points. */
export const ribbon = (x0, y0, x1, y1, thickness) => {
  const mid = (x0 + x1) / 2
  return `M${x0},${y0}C${mid},${y0} ${mid},${y1} ${x1},${y1}L${x1},${y1 + thickness}C${mid},${y1 + thickness} ${mid},${y0 + thickness} ${x0},${y0 + thickness}Z`
}

/**
 * Positions for the flow, `width` wide: the total `hubHeight` tall in the middle, each side's bars
 * down the edges and a ribbon for each line. Each bar has a slot at least `slot(line)` tall (its
 * label's height) and `gap` more than the bar, with the bar centred in it, so a label can sit
 * beside its own bar. The box is as tall as the taller side needs. `inset` is the room each side
 * keeps for labels outside the bars (0 when they are drawn over the ribbons).
 */
export const layoutFlow = (statement, { width, hubHeight, inset = 0, gap = 6, node = 10, pad = 4, slot = () => 0 }) => {
  const { sources, uses, total, revenue, expense } = flowColumns(statement)
  const scale = hubHeight / total
  const slots = (lines) => lines.map((line) => Math.max(line.actual * scale + gap, slot(line)))
  const spans = [sources, uses].map((lines) => slots(lines).reduce((sum, each) => sum + each, 0))
  const height = Math.ceil(Math.max(hubHeight, ...spans) + pad * 2)
  const xLeft = inset
  const xRight = width - inset - node
  const xHub = (width - node) / 2
  const hubTop = (height - hubHeight) / 2
  const column = (lines, x, span) => {
    const sizes = slots(lines)
    let y = (height - span) / 2
    let along = hubTop
    return lines.map((line, at) => {
      const size = line.actual * scale
      const placed = { ...line, x, y: y + (sizes[at] - size) / 2, size, hubY: along, slotTop: y, slotSize: sizes[at] }
      y += sizes[at]
      along += size
      return placed
    })
  }
  const left = column(sources, xLeft, spans[0])
  const right = column(uses, xRight, spans[1])
  return {
    revenue, expense, total, height,
    hub: { x: xHub, y: hubTop, size: hubHeight },
    sources: left.map((line) => ({ ...line, path: ribbon(xLeft + node, line.y, xHub, line.hubY, line.size) })),
    uses: right.map((line) => ({ ...line, path: ribbon(xHub + node, line.hubY, xRight, line.y, line.size) })),
    node
  }
}

/** The trend's points: total revenue and expense, as first published, for every year. */
export const trendSeries = () => BUDGET_STATEMENTS.map((statement) => ({
  year: statement.year,
  revenue: statement.revenue.total.actual,
  expense: statement.expense.total.actual,
  surplus: statement.surplus.actual
}))

/** Round axis steps for a maximum in $ millions: every 10, 20 or 25 billion. */
export const axisTicks = (max) => {
  const step = [5000, 10000, 20000, 25000, 50000].find((each) => max / each <= 5) ?? 50000
  const ticks = []
  for (let value = 0; value <= max + step * 0.001; value += step) ticks.push(value)
  if (ticks.at(-1) < max) ticks.push(ticks.at(-1) + step)
  return ticks
}
