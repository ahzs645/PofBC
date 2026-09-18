// Just enough SVG path arithmetic to move artwork to a new origin.
//
// The three source lockups each carry their own copy of the provincial mark, drawn at the same
// size but parked at a different spot on a shared 3673×2318 artboard. To prove they really are one
// drawing — and to store that drawing once, at its own origin — the coordinates have to be
// shifted, not merely wrapped in a <g transform>: two paths can only be compared for equality
// once they are expressed in the same space.

// Path data is a stream of command letters, each followed by a fixed-size group of numbers,
// repeated. This table gives the group size and which slots inside a group are coordinates.
const COMMANDS = {
  M: { size: 2, x: [0], y: [1] },
  L: { size: 2, x: [0], y: [1] },
  H: { size: 1, x: [0], y: [] },
  V: { size: 1, x: [], y: [0] },
  C: { size: 6, x: [0, 2, 4], y: [1, 3, 5] },
  S: { size: 4, x: [0, 2], y: [1, 3] },
  Q: { size: 4, x: [0, 2], y: [1, 3] },
  T: { size: 2, x: [0], y: [1] },
  // Arc: rx ry rotation large-arc sweep x y — only the final pair is a position.
  A: { size: 7, x: [5], y: [6] },
  Z: { size: 0, x: [], y: [] }
}

const NUMBER = /-?(?:\d+\.?\d*|\.\d+)(?:[eE][-+]?\d+)?/g

/** Splits path data into `{ command, values }` groups, one per parameter set. */
export const parsePath = (data) => {
  const groups = []

  for (const [, letter, body] of data.matchAll(/([MmLlHhVvCcSsQqTtAaZz])([^MmLlHhVvCcSsQqTtAaZz]*)/g)) {
    const spec = COMMANDS[letter.toUpperCase()]
    const numbers = (body.match(NUMBER) || []).map(Number)

    if (spec.size === 0) {
      groups.push({ command: letter, values: [] })
      continue
    }

    // A repeated parameter group implies the command again, except that a repeated moveto is an
    // implicit lineto — the one place where the letter changes between groups.
    for (let i = 0; i < numbers.length; i += spec.size) {
      const isRepeat = i > 0
      const command = isRepeat && letter === 'M' ? 'L' : isRepeat && letter === 'm' ? 'l' : letter
      groups.push({ command, values: numbers.slice(i, i + spec.size) })
    }
  }

  return groups
}

// Numbers are emitted at the precision the artwork was authored with. Two decimal places is what
// Illustrator wrote for these files, and keeping it avoids inflating the asset with noise digits.
const format = (value) => {
  const rounded = Math.round(value * 100) / 100
  return String(rounded).replace(/^(-?)0\./, '$1.')
}

export const serializePath = (groups) => groups
  .map(({ command, values }) => command + values.map(format).join(' ').replace(/ -/g, '-'))
  .join('')
  .replace(/([\d.])([A-Za-z])/g, '$1$2')

/**
 * Shifts a path's absolute coordinates by (dx, dy). Relative commands describe offsets from the
 * previous point, so they are already translation-invariant and are passed through untouched —
 * which is exactly why two copies of the same drawing differ only in their opening moveto.
 */
export const translatePath = (data, dx, dy) => serializePath(
  parsePath(data).map(({ command, values }) => {
    if (command !== command.toUpperCase()) return { command, values } // relative: unchanged

    const spec = COMMANDS[command.toUpperCase()]
    const shifted = [...values]
    spec.x.forEach((index) => { shifted[index] += dx })
    spec.y.forEach((index) => { shifted[index] += dy })

    return { command, values: shifted }
  })
)

/** Shifts the `points` list of a <polygon>/<polyline>, which is a flat run of x y pairs. */
export const translatePoints = (points, dx, dy) => {
  const numbers = (points.match(NUMBER) || []).map(Number)
  const moved = numbers.map((value, index) => value + (index % 2 === 0 ? dx : dy))
  const pairs = []
  for (let i = 0; i < moved.length; i += 2) pairs.push(`${format(moved[i])} ${format(moved[i + 1])}`)
  return pairs.join(' ')
}

// ── Bounding box ────────────────────────────────────────────────────────────────────────────────

// A cubic segment's extremes are at its endpoints and wherever its derivative crosses zero, so the
// box is exact rather than the loose control-point hull. The lockups centre and baseline-align
// against the mark's box, so a few units of slop here would show up as visible misalignment.
const cubicExtremes = (p0, p1, p2, p3) => {
  const values = [p0, p3]
  const a = -p0 + 3 * p1 - 3 * p2 + p3
  const b = 2 * (p0 - 2 * p1 + p2)
  const c = p1 - p0

  const roots = Math.abs(a) < 1e-12
    ? (Math.abs(b) < 1e-12 ? [] : [-c / b])
    : (() => {
        const discriminant = b * b - 4 * a * c
        if (discriminant < 0) return []
        const root = Math.sqrt(discriminant)
        return [(-b + root) / (2 * a), (-b - root) / (2 * a)]
      })()

  for (const t of roots) {
    if (t <= 0 || t >= 1) continue
    const u = 1 - t
    values.push(u * u * u * p0 + 3 * u * u * t * p1 + 3 * u * t * t * p2 + t * t * t * p3)
  }

  return values
}

// A quadratic's single extreme, where its derivative crosses zero. TrueType glyph outlines are
// quadratic throughout, so measuring outlined type needs this as much as the mark needed cubics.
const quadraticExtremes = (p0, p1, p2) => {
  const values = [p0, p2]
  const denominator = p0 - 2 * p1 + p2

  if (Math.abs(denominator) > 1e-12) {
    const t = (p0 - p1) / denominator
    if (t > 0 && t < 1) {
      const u = 1 - t
      values.push(u * u * p0 + 2 * u * t * p1 + t * t * p2)
    }
  }

  return values
}

/** Exact bounding box of path data, as `{ minX, minY, maxX, maxY }`. */
export const pathBounds = (data) => {
  let minX = Infinity; let minY = Infinity; let maxX = -Infinity; let maxY = -Infinity
  let x = 0; let y = 0           // current point
  let startX = 0; let startY = 0 // subpath start, for Z
  let lastControl = null         // trailing control point of the previous curve, for S and T

  const include = (px, py) => {
    minX = Math.min(minX, px); maxX = Math.max(maxX, px)
    minY = Math.min(minY, py); maxY = Math.max(maxY, py)
  }

  const curve = (x1, y1, x2, y2, x3, y3) => {
    for (const value of cubicExtremes(x, x1, x2, x3)) { minX = Math.min(minX, value); maxX = Math.max(maxX, value) }
    for (const value of cubicExtremes(y, y1, y2, y3)) { minY = Math.min(minY, value); maxY = Math.max(maxY, value) }
    lastControl = { x: x2, y: y2 }
    x = x3; y = y3
  }

  const quadratic = (x1, y1, x2, y2) => {
    for (const value of quadraticExtremes(x, x1, x2)) { minX = Math.min(minX, value); maxX = Math.max(maxX, value) }
    for (const value of quadraticExtremes(y, y1, y2)) { minY = Math.min(minY, value); maxY = Math.max(maxY, value) }
    lastControl = { x: x1, y: y1 }
    x = x2; y = y2
  }

  for (const { command, values } of parsePath(data)) {
    const relative = command !== command.toUpperCase()
    const upper = command.toUpperCase()
    const [ox, oy] = relative ? [x, y] : [0, 0]

    if (!'CSQT'.includes(upper)) lastControl = null

    switch (upper) {
      case 'M':
        x = values[0] + ox; y = values[1] + oy
        startX = x; startY = y
        include(x, y)
        break
      case 'L':
        x = values[0] + ox; y = values[1] + oy
        include(x, y)
        break
      case 'H':
        x = values[0] + ox
        include(x, y)
        break
      case 'V':
        y = values[0] + oy
        include(x, y)
        break
      case 'C':
        curve(values[0] + ox, values[1] + oy, values[2] + ox, values[3] + oy, values[4] + ox, values[5] + oy)
        break
      case 'S': {
        // The first control point mirrors the previous curve's second one about the current point.
        const x1 = lastControl ? 2 * x - lastControl.x : x
        const y1 = lastControl ? 2 * y - lastControl.y : y
        curve(x1, y1, values[0] + ox, values[1] + oy, values[2] + ox, values[3] + oy)
        break
      }
      case 'Q':
        quadratic(values[0] + ox, values[1] + oy, values[2] + ox, values[3] + oy)
        break
      case 'T': {
        // The control point mirrors the previous quadratic's about the current point.
        const x1 = lastControl ? 2 * x - lastControl.x : x
        const y1 = lastControl ? 2 * y - lastControl.y : y
        quadratic(x1, y1, values[0] + ox, values[1] + oy)
        break
      }
      case 'Z':
        x = startX; y = startY
        break
      default:
        throw new Error(`pathBounds does not handle "${command}"`)
    }
  }

  return { minX, minY, maxX, maxY }
}
