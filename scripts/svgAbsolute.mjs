// Path data reduced to absolute M, L, C and Z, and the boxes of the result.
//
// scripts/svgPath.mjs moves artwork that is already tidy. The files here are not: they come out of
// a PDF-to-SVG converter and an optimiser, which between them use everything the format has.
// Anything that lifts letters or shapes out of that kind of file goes through this.

const SIZES = { M: 2, L: 2, H: 1, V: 1, C: 6, S: 4, Q: 4, T: 2, A: 7, Z: 0 }
const NUMBER = /^[\s,]*(-?(?:\d+\.?\d*|\.\d+)(?:[eE][-+]?\d+)?)/

function * tokens (data) {
  for (const [, letter, body] of data.matchAll(/([MmLlHhVvCcSsQqTtAaZz])([^MmLlHhVvCcSsQqTtAaZz]*)/g)) {
    const size = SIZES[letter.toUpperCase()]
    if (!size) { yield [letter, []]; continue }

    // An arc's two flags are single digits and optimisers pack them against their neighbours
    // ("a.46.46 0 0 1-.477"), so they are read one character at a time.
    const values = []
    let rest = body
    while (rest.replace(/[\s,]/g, '')) {
      if (letter.toUpperCase() === 'A' && [3, 4].includes(values.length % 7)) {
        rest = rest.replace(/^[\s,]*/, '')
        values.push(Number(rest[0]))
        rest = rest.slice(1)
      } else {
        const match = NUMBER.exec(rest)
        values.push(Number(match[1]))
        rest = rest.slice(match[0].length)
      }
    }

    for (let i = 0; i < values.length; i += size) {
      const repeat = i > 0 && letter.toUpperCase() === 'M'
      yield [repeat ? (letter === 'M' ? 'L' : 'l') : letter, values.slice(i, i + size)]
    }
  }
}

/** An elliptical arc as cubic Béziers, a quarter turn or less apiece. */
export function arcToCubics (x1, y1, rx, ry, rotation, large, sweep, x2, y2) {
  if (!rx || !ry) return [[x1, y1, x2, y2, x2, y2]]
  const phi = rotation * Math.PI / 180
  const cos = Math.cos(phi)
  const sin = Math.sin(phi)
  const hx = (x1 - x2) / 2
  const hy = (y1 - y2) / 2
  const xp = cos * hx + sin * hy
  const yp = -sin * hx + cos * hy
  rx = Math.abs(rx); ry = Math.abs(ry)
  const lambda = xp ** 2 / rx ** 2 + yp ** 2 / ry ** 2
  if (lambda > 1) { rx *= Math.sqrt(lambda); ry *= Math.sqrt(lambda) }
  const num = rx * rx * ry * ry - rx * rx * yp * yp - ry * ry * xp * xp
  const den = rx * rx * yp * yp + ry * ry * xp * xp
  let k = den ? Math.sqrt(Math.max(0, num / den)) : 0
  if (large === sweep) k = -k
  const cxp = k * rx * yp / ry
  const cyp = -k * ry * xp / rx
  const cx = cos * cxp - sin * cyp + (x1 + x2) / 2
  const cy = sin * cxp + cos * cyp + (y1 + y2) / 2
  const angle = (ux, uy, vx, vy) => Math.atan2(ux * vy - uy * vx, ux * vx + uy * vy)
  const start = angle(1, 0, (xp - cxp) / rx, (yp - cyp) / ry)
  let delta = angle((xp - cxp) / rx, (yp - cyp) / ry, (-xp - cxp) / rx, (-yp - cyp) / ry)
  if (!sweep && delta > 0) delta -= 2 * Math.PI
  if (sweep && delta < 0) delta += 2 * Math.PI

  const count = Math.max(1, Math.ceil(Math.abs(delta) / (Math.PI / 2)))
  const step = delta / count
  const handle = 4 / 3 * Math.tan(step / 4)
  const point = (t) => [cos * rx * Math.cos(t) - sin * ry * Math.sin(t) + cx, sin * rx * Math.cos(t) + cos * ry * Math.sin(t) + cy]
  const slope = (t) => [-cos * rx * Math.sin(t) - sin * ry * Math.cos(t), -sin * rx * Math.sin(t) + cos * ry * Math.cos(t)]

  const out = []
  for (let i = 0; i < count; i += 1) {
    const a = start + i * step
    const b = a + step
    const [p0x, p0y] = point(a)
    const [p3x, p3y] = point(b)
    const [d0x, d0y] = slope(a)
    const [d3x, d3y] = slope(b)
    out.push([p0x + handle * d0x, p0y + handle * d0y, p3x - handle * d3x, p3y - handle * d3y, p3x, p3y])
  }
  out.at(-1).splice(4, 2, x2, y2)
  return out
}

/** Path data as subpaths of absolute ['M'|'L', x, y], ['C', …6] and ['Z']. */
export function absolute (data) {
  const subpaths = []
  let current
  let x = 0; let y = 0; let startX = 0; let startY = 0
  let control = null; let quad = null; let previous = null

  for (const [letter, v] of tokens(data)) {
    const command = letter.toUpperCase()
    const relative = letter !== command
    const ox = relative ? x : 0
    const oy = relative ? y : 0
    const curve = (c1x, c1y, c2x, c2y, ex, ey) => { current.push(['C', c1x, c1y, c2x, c2y, ex, ey]); x = ex; y = ey }
    const quadratic = (qx, qy, ex, ey) => {
      curve(x + 2 / 3 * (qx - x), y + 2 / 3 * (qy - y), ex + 2 / 3 * (qx - ex), ey + 2 / 3 * (qy - ey), ex, ey)
      quad = [qx, qy]
    }

    if (command === 'M') { x = v[0] + ox; y = v[1] + oy; startX = x; startY = y; current = [['M', x, y]]; subpaths.push(current) }
    else if (command === 'Z') { current.push(['Z']); x = startX; y = startY }
    else if (command === 'L') { x = v[0] + ox; y = v[1] + oy; current.push(['L', x, y]) }
    else if (command === 'H') { x = v[0] + (relative ? x : 0); current.push(['L', x, y]) }
    else if (command === 'V') { y = v[0] + (relative ? y : 0); current.push(['L', x, y]) }
    else if (command === 'C') curve(v[0] + ox, v[1] + oy, v[2] + ox, v[3] + oy, v[4] + ox, v[5] + oy)
    else if (command === 'S') {
      const [c1x, c1y] = (previous === 'C' || previous === 'S') && control ? [2 * x - control[0], 2 * y - control[1]] : [x, y]
      curve(c1x, c1y, v[0] + ox, v[1] + oy, v[2] + ox, v[3] + oy)
    } else if (command === 'Q') quadratic(v[0] + ox, v[1] + oy, v[2] + ox, v[3] + oy)
    else if (command === 'T') {
      const [qx, qy] = (previous === 'Q' || previous === 'T') && quad ? [2 * x - quad[0], 2 * y - quad[1]] : [x, y]
      quadratic(qx, qy, v[0] + ox, v[1] + oy)
    } else if (command === 'A') {
      for (const segment of arcToCubics(x, y, v[0], v[1], v[2], v[3], v[4], v[5] + ox, v[6] + oy)) curve(...segment)
    }

    control = command === 'C' || command === 'S' ? [current.at(-1)[3], current.at(-1)[4]] : null
    previous = command
  }
  return subpaths
}

/** A subpath's box, from its on-curve points and enough samples along each curve. */
export function boundsOf (subpath) {
  const xs = []; const ys = []
  let x = 0; let y = 0
  for (const [command, ...v] of subpath) {
    if (command === 'M' || command === 'L') { x = v[0]; y = v[1]; xs.push(x); ys.push(y) }
    if (command === 'C') {
      for (let i = 1; i <= 16; i += 1) {
        const t = i / 16; const u = 1 - t
        xs.push(u ** 3 * x + 3 * u * u * t * v[0] + 3 * u * t * t * v[2] + t ** 3 * v[4])
        ys.push(u ** 3 * y + 3 * u * u * t * v[1] + 3 * u * t * t * v[3] + t ** 3 * v[5])
      }
      x = v[4]; y = v[5]
    }
  }
  return { left: Math.min(...xs), top: Math.min(...ys), right: Math.max(...xs), bottom: Math.max(...ys) }
}
