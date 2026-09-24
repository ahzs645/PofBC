// Lifts the letters the 46 current marks never use out of other marks the Province published.
//
// src/current/nameGlyphs.js is every letter the current ministry names happen to contain, and
// nothing else: no capital N, no O, no B. The historical names the ministry list now offers need
// them — "Forests, Lands, Natural Resource Operations and Rural Development" was drawn with holes
// where its N and O belonged. Older marks, drawn by the Province in the same Adobe Garamond at the
// same tracking, do contain them, so the missing capitals can come from the Province's own artwork
// rather than from a font.
//
// Each file in artwork/current/lifted/ is one such mark, listed in its index.json with the wording
// it draws, line by line. For every line this fits the type size and origin against the committed
// metrics — using the letters already in the alphabet as the reference — then moves each letter the
// alphabet lacks onto the same 1000-unit em and pen origin nameGlyphs.js uses. The fit is reported,
// and a file whose letters do not land where the metrics say they should is refused rather than
// trusted.
//
// Writes src/current/liftedGlyphs.js. Committed, for the same reason nameGlyphs.js is: it is the
// Province's drawing, not a typeface.
//
// Run: npm run lift:current-letters

import { readFileSync, writeFileSync } from 'node:fs'
import { resolve, dirname } from 'node:path'
import { fileURLToPath } from 'node:url'
import published from '../src/current/nameGlyphs.js'
import { EXTENTS, KERNING, TRACKING, WIDTHS } from '../src/current/nameMetrics.js'

const root = resolve(dirname(fileURLToPath(import.meta.url)), '..')
const LIFTED = resolve(root, 'artwork/current/lifted')
const target = resolve(root, 'src/current/liftedGlyphs.js')

/** Worst disagreement, in points, between where a known letter is drawn and where it should be. */
const TOLERANCE = 0.02

// ── Path data to absolute M/L/C ──────────────────────────────────────────────────────────────────
//
// These files come out of a PDF-to-SVG converter and an optimiser, so they use everything the
// format has: relative commands, shorthand curves, quadratics and elliptical arcs. The alphabet
// stores absolute M, L, C and Z only, so all of it is reduced to those.

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
function arcToCubics (x1, y1, rx, ry, rotation, large, sweep, x2, y2) {
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
function absolute (data) {
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
function boundsOf (subpath) {
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

// ── Setting the wording, as the app does ─────────────────────────────────────────────────────────

/** Each non-space character of a line, with where its pen sits in 1/1000 em. */
function pensOf (text) {
  const out = []
  let pen = 0
  ;[...text].forEach((character, index) => {
    if (character !== ' ') out.push({ character, pen })
    pen += WIDTHS[character]
    const next = text[index + 1]
    if (next !== undefined) pen += TRACKING + (KERNING[character + next] ?? 0)
  })
  return out
}

const median = (values) => {
  const sorted = [...values].sort((a, b) => a - b)
  const half = sorted.length >> 1
  return sorted.length % 2 ? sorted[half] : (sorted[half - 1] + sorted[half]) / 2
}

const round = (value) => {
  const text = String(Math.round(value * 10) / 10).replace(/^(-?)0\./, '$1.')
  return text === '-0' ? '0' : text
}

// ── Lift ─────────────────────────────────────────────────────────────────────────────────────────

const manifest = JSON.parse(readFileSync(resolve(LIFTED, 'index.json'), 'utf8'))
const lifted = {}

for (const entry of manifest) {
  const source = readFileSync(resolve(LIFTED, entry.file), 'utf8')
  const expected = entry.lines.map((line) => line.replace(/ /g, '').length)

  // The wording is the one path whose subpaths make up every letter; the mark's own shapes sit to
  // the left of the divider. Every path is considered and only the letters to the right are kept.
  const contours = [...source.matchAll(/<path\b[^>]*\sd="([^"]+)"/g)]
    .flatMap((match) => absolute(match[1]))
    .map((subpath) => ({ subpath, box: boundsOf(subpath) }))
  const divider = Math.max(...contours
    .filter(({ box }) => box.right - box.left < 1 && box.bottom - box.top > 20)
    .map(({ box }) => box.right))
  const wording = contours.filter(({ box }) => box.left > divider)

  // Lines, by where each contour's middle sits: the rows are a leading apart, which no letter's
  // own height comes near, so the gaps between them are unambiguous.
  const middles = wording.map(({ box }) => (box.top + box.bottom) / 2).sort((a, b) => a - b)
  const rows = [[middles[0]]]
  for (const middle of middles.slice(1)) {
    if (middle - rows.at(-1).at(-1) > 3) rows.push([middle])
    else rows.at(-1).push(middle)
  }
  if (rows.length !== entry.lines.length) {
    throw new Error(`${entry.file}: found ${rows.length} lines of wording, expected ${entry.lines.length}`)
  }
  const rowOf = (box) => {
    const middle = (box.top + box.bottom) / 2
    return rows.findIndex((row) => middle >= row[0] - 0.01 && middle <= row.at(-1) + 0.01)
  }

  entry.lines.forEach((text, index) => {
    // Letters: a counter, a dot or an accent sits over the letter it belongs to.
    const letters = []
    const members = wording.filter(({ box }) => rowOf(box) === index).sort((a, b) => a.box.left - b.box.left)
    for (const contour of members) {
      const owner = letters.find(({ box }) => {
        const overlap = Math.min(box.right, contour.box.right) - Math.max(box.left, contour.box.left)
        return overlap > 0.6 * Math.min(box.right - box.left, contour.box.right - contour.box.left)
      })
      if (owner) {
        owner.subpaths.push(contour.subpath)
        owner.box = {
          left: Math.min(owner.box.left, contour.box.left),
          top: Math.min(owner.box.top, contour.box.top),
          right: Math.max(owner.box.right, contour.box.right),
          bottom: Math.max(owner.box.bottom, contour.box.bottom)
        }
      } else letters.push({ subpaths: [contour.subpath], box: { ...contour.box } })
    }
    letters.sort((a, b) => a.box.left - b.box.left)
    if (letters.length !== expected[index]) {
      throw new Error(`${entry.file} line ${index + 1}: found ${letters.length} letters, "${text}" has ${expected[index]}`)
    }

    // Size and origin, by least squares on where the known letters' ink starts and ends. A letter
    // the alphabet already has is a reference; one it lacks is what is being lifted, so it has no
    // say in where it is put.
    const pens = pensOf(text)
    const known = pens.map((p, i) => ({ ...p, drawn: letters[i] })).filter(({ character }) => published[character])
    const samples = known.flatMap(({ character, pen, drawn }) => [
      [(pen + EXTENTS[character][0]) / 1000, drawn.box.left],
      [(pen + EXTENTS[character][1]) / 1000, drawn.box.right]
    ])
    const mx = samples.reduce((sum, [a]) => sum + a, 0) / samples.length
    const my = samples.reduce((sum, [, b]) => sum + b, 0) / samples.length
    const size = samples.reduce((sum, [a, b]) => sum + (a - mx) * (b - my), 0) /
      samples.reduce((sum, [a]) => sum + (a - mx) ** 2, 0)
    const origin = my - size * mx
    const worst = Math.max(...samples.map(([a, b]) => Math.abs(origin + size * a - b)))
    const baseline = median(known.map(({ character, drawn }) => drawn.box.bottom - size * EXTENTS[character][3] / 1000))

    if (worst > TOLERANCE) {
      throw new Error(`${entry.file} line ${index + 1}: the known letters sit up to ${worst.toFixed(3)} pt off ` +
        'the metrics, so this is not the alphabet the current marks are set in')
    }
    console.log(`  ${entry.file}  "${text}"  ${size.toFixed(3)} pt, worst ${(worst * 1000 / size).toFixed(1)}/1000 em`)

    pens.forEach(({ character, pen }, i) => {
      if (published[character] || lifted[character]) return
      const penX = origin + size * pen / 1000
      const k = 1000 / size
      lifted[character] = letters[i].subpaths.map((subpath) => subpath.map(([command, ...v]) => command +
        v.map((value, j) => round(j % 2 === 0 ? (value - penX) * k : (value - baseline) * k)).join(' ')
      ).join('')).join('').replace(/ -/g, '-')
    })
  })
}

const sorted = Object.fromEntries(Object.entries(lifted).sort(([a], [b]) => (a < b ? -1 : 1)))

writeFileSync(target, `// Generated by scripts/lift-current-letters.mjs — do not edit.
//
// Letters the Province's current ministry marks never use, lifted from older marks it published in
// the same alphabet — see artwork/current/lifted/. Same em, origin and direction as nameGlyphs.js:
// 1/1000 em, baseline at y=0, y running downward.

export default {
${Object.entries(sorted).map(([character, d]) => `  ${JSON.stringify(character)}: ${JSON.stringify(d)}`).join(',\n')}
}
`)

console.log(`  lifted      ${Object.keys(sorted).join(' ') || 'nothing'}`)
