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
import { TRACKING } from '../src/current/nameMetrics.js'
import { absolute, boundsOf } from './svgAbsolute.mjs'
import { fitLine, groupLetters } from './letterFit.mjs'

const root = resolve(dirname(fileURLToPath(import.meta.url)), '..')
const LIFTED = resolve(root, 'artwork/current/lifted')
const target = resolve(root, 'src/current/liftedGlyphs.js')

/**
 * Worst disagreement, in 1/1000 em, between where a known letter is drawn and where it should be.
 *
 * Measured per line, against the metrics the app sets with. The FLNRORD mark agrees to 0.6 and the
 * WelcomeBC wordmark to 3.3; a line set in another face, or without its kerning, misses by tens.
 */
const TOLERANCE = 4

const round = (value) => {
  const text = String(Math.round(value * 10) / 10).replace(/^(-?)0\./, '$1.')
  return text === '-0' ? '0' : text
}

// ── Lift ─────────────────────────────────────────────────────────────────────────────────────────

const manifest = JSON.parse(readFileSync(resolve(LIFTED, 'index.json'), 'utf8'))
const lifted = {}

for (const entry of manifest) {
  // Only what is drawn: clip paths live in <defs>, and a clip rectangle is not a letter.
  const source = readFileSync(resolve(LIFTED, entry.file), 'utf8').replace(/<defs>[\s\S]*?<\/defs>/g, '')
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
    const letters = groupLetters(wording.filter(({ box }) => rowOf(box) === index))
    if (letters.length !== expected[index]) {
      throw new Error(`${entry.file} line ${index + 1}: found ${letters.length} letters, "${text}" has ${expected[index]}`)
    }

    // A letter the alphabet already has is a reference; one it lacks is what is being lifted, so
    // it has no say in where it is put.
    const { size, origin, baseline, worst, pens } = fitLine({
      text, letters, tracking: entry.tracking ?? TRACKING, isReference: (character) => Boolean(published[character])
    })

    if (worst > TOLERANCE) {
      throw new Error(`${entry.file} line ${index + 1}: the known letters sit up to ` +
        `${worst.toFixed(1)}/1000 em off the metrics, so this is not the alphabet the ` +
        'current marks are set in, or not at the tracking index.json gives it')
    }
    console.log(`  ${entry.file}  "${text}"  ${size.toFixed(3)} pt, worst ${worst.toFixed(1)}/1000 em`)

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
