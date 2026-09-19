// Stores the BC mark once per language, with the geometry a ministry name is set against.
//
// All 46 published marks embed the same drawing — the sun, the mountains and the wordmark — and
// differ only in the name beside it. English and French are two drawings rather than one, because
// the wordmark itself reads COLOMBIE-BRITANNIQUE in French and is wider.
//
// Alongside the artwork this records where the name goes: the rule between them, the gap either
// side of it, and the baseline the wording sits on. Those are measured across every mark rather
// than read off one of them, so a single file drawn slightly off-register cannot set the standard.
//
// Run: npm run build:current-mark

import { existsSync, readFileSync, writeFileSync } from 'node:fs'
import { resolve, dirname } from 'node:path'
import { fileURLToPath } from 'node:url'
import { pathBounds } from './svgPath.mjs'

const root = resolve(dirname(fileURLToPath(import.meta.url)), '..')
const MARKS = resolve(root, 'public/current-marks')

const fitPath = resolve(root, 'scripts/current-fit.json')
if (!existsSync(fitPath)) {
  console.error('\nRun `npm run verify:current-names` first — it measures the fit this builds on.\n')
  process.exit(1)
}

const { leading, marks } = JSON.parse(readFileSync(fitPath, 'utf8'))

const MARK_ROLES = ['sun', 'mountains', 'knockout', 'wordmark']

const median = (values) => {
  const sorted = [...values].sort((a, b) => a - b)
  const half = sorted.length >> 1
  return sorted.length % 2 ? sorted[half] : (sorted[half - 1] + sorted[half]) / 2
}

/** The mark's own shapes, the divider, and the wordmark's baseline, from one published file. */
function readMark (key) {
  const source = readFileSync(resolve(MARKS, `${key}.svg`), 'utf8')

  const group = /<g transform="translate\(([-\d.]+) ([-\d.]+)\)">((?:(?!<\/g>).)*?data-role="wordmark".*?)<\/g>/s
    .exec(source)
  const tx = Number(group[1])
  const ty = Number(group[2])

  const shapes = []
  const feet = []
  let right = 0
  for (const element of group[3].matchAll(/<path[^>]*data-role="(\w+)"[^>]*\sd="([^"]+)"[^>]*\/>/g)) {
    const [, role, d] = element
    if (!MARK_ROLES.includes(role)) continue
    const box = pathBounds(d)
    shapes.push({ role, d, tx, ty })
    right = Math.max(right, box.maxX + tx)
    if (role === 'wordmark') feet.push(box.maxY + ty)
  }

  const rect = /<rect data-role="divider"([^>]*)\/>/.exec(source)
  const divider = Object.fromEntries([...rect[1].matchAll(/\s(x|y|width|height)="([^"]+)"/g)]
    .map(([, name, value]) => [name, Number(value)]))

  // The wordmark is two lines — BRITISH over COLUMBIA, COLOMBIE- over BRITANNIQUE — and it is the
  // lower one the ministry name aligns to. So: cluster the feet into lines, take the bottom line,
  // and use its median, which shrugs off the slight overshoot of the round letters.
  const sorted = [...feet].sort((a, b) => a - b)
  const lines = [[sorted[0]]]
  for (const foot of sorted.slice(1)) {
    if (foot - lines.at(-1).at(-1) > 1) lines.push([])
    lines.at(-1).push(foot)
  }
  const baseline = median(lines.at(-1))

  return { shapes, divider, right, baseline, tx, ty }
}

/** Two marks are the same drawing when every coordinate agrees to within the source's rounding. */
function sameDrawing (a, b) {
  if (a.shapes.length !== b.shapes.length) return false
  return a.shapes.every((shape, i) => {
    const other = b.shapes[i]
    if (shape.role !== other.role) return false
    const one = shape.d.match(/-?\d+\.?\d*/g).map(Number)
    const two = other.d.match(/-?\d+\.?\d*/g).map(Number)
    return one.length === two.length && one.every((value, n) => Math.abs(value - two[n]) <= 0.02)
  })
}

const out = {}
const report = []

for (const language of ['en', 'fr']) {
  const keys = Object.keys(marks).filter((key) => key.endsWith(`-${language}`))
  const read = keys.map((key) => ({ key, ...readMark(key) }))

  // Group by drawing and take the largest group; a lone file that disagrees is a file with a
  // problem, not a second official mark.
  const groups = []
  for (const mark of read) {
    const group = groups.find((g) => sameDrawing(g[0], mark))
    if (group) group.push(mark)
    else groups.push([mark])
  }
  groups.sort((a, b) => b.length - a.length)
  const [agreed, ...odd] = groups
  const canonical = agreed[0]

  const sizes = agreed.map((m) => marks[m.key].size)
  const size = median(sizes)
  const dividerX = median(agreed.map((m) => m.divider.x))
  const nameX = median(agreed.map((m) => marks[m.key].origin))
  const baseline = median(agreed.map((m) => m.baseline))

  out[language] = {
    width: Number(canonical.right.toFixed(3)),
    height: Number(median(agreed.map((m) => m.divider.height)).toFixed(3)),
    shapes: canonical.shapes.map(({ role, d, tx, ty }) => ({
      role,
      // Baked into the mark's own space so nothing downstream needs a transform.
      d: shift(d, tx, ty)
    })),
    divider: {
      x: Number(dividerX.toFixed(3)),
      width: Number(median(agreed.map((m) => m.divider.width)).toFixed(3)),
      height: Number(median(agreed.map((m) => m.divider.height)).toFixed(3))
    },
    nameX: Number(nameX.toFixed(3)),
    baseline: Number(baseline.toFixed(3)),
    size: Number(size.toFixed(3))
  }

  report.push({
    language,
    agreed: agreed.length,
    of: read.length,
    odd: odd.flat().map((m) => m.key),
    gapBefore: dividerX - canonical.right,
    gapAfter: nameX - (dividerX + canonical.divider.width)
  })
}

function shift (d, dx, dy) {
  let i = 0
  return d.replace(/-?\d+\.?\d*/g, (value) => {
    const moved = Number(value) + (i % 2 === 0 ? dx : dy)
    i += 1
    return String(Math.round(moved * 1000) / 1000)
  })
}

writeFileSync(resolve(root, 'src/assets/currentMark.js'), `// Generated by scripts/build-current-mark.mjs — do not edit.
//
// The Province's BC mark, lifted unchanged from the published ministry marks and stored once per
// language. Every published mark embeds this same drawing; only the ministry name beside it
// differs, and that is now typeset rather than stored.
//
// Coordinates are in PDF points from the mark's own top-left corner. \`divider\` is the gold rule
// between the mark and the name, \`nameX\` is where the name's first letter begins its advance, and
// \`baseline\` is the baseline of the wordmark — which the name's *last* line sits on, so a name
// grows upward as it gains lines.

export const CURRENT_MARK = ${JSON.stringify(out, null, 2)}

/** Leading between a name's lines, in points. The marks are set solid. */
export const NAME_LEADING = ${leading}
`)

for (const r of report) {
  console.log(`  ${r.language}  ${String(r.agreed).padStart(2)}/${r.of} marks share one drawing   ` +
    `mark→rule ${r.gapBefore.toFixed(2)}  rule→name ${r.gapAfter.toFixed(2)}  ` +
    `${out[r.language].size} pt on a ${out[r.language].baseline} baseline`)
  if (r.odd.length) console.log(`      drawn differently: ${r.odd.join(', ')}`)
}
const bytes = JSON.stringify(out).length
console.log(`  → src/assets/currentMark.js  (${(bytes / 1024).toFixed(1)} KB)`)
