// Consolidates the provincial mark out of the source artwork into a single reusable asset.
//
// artwork/lockup-{stacked,centred,horizontal}.svg are three exports of the same Illustrator
// artboard, and each carries its own full copy of the mark — roughly 19 KB of identical path data,
// three times over, at three different positions on the board. This script proves they are one
// drawing and writes it out once, normalised to its own origin, as src/assets/markup.js.
//
// The proof matters more than the saving: it is what licenses the rest of the codebase to treat
// "the mark" as a single thing. If a future artwork drop changes one lockup's mark and not the
// others, this build fails loudly instead of silently blessing whichever file was read first.
//
// Run: npm run build:mark

import { readFileSync, writeFileSync } from 'node:fs'
import { dirname, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'
import { parsePath, pathBounds, translatePath, translatePoints } from './svgPath.mjs'

const root = resolve(dirname(fileURLToPath(import.meta.url)), '..')

const SOURCES = ['lockup-stacked.svg', 'lockup-centred.svg', 'lockup-horizontal.svg']

// Illustrator wrote these files with two decimal places of precision, and each lockup sits at a
// different offset on the artboard, so the same point can land on either side of a rounding
// boundary between files. Anything within one quantisation step is the same coordinate.
const COORDINATE_TOLERANCE = 0.011

// The generated class names that carry `fill-rule: evenodd` in the source stylesheets. Every other
// mark shape is a plain solid fill.
const EVENODD_CLASS = 'cls-1'

const SHAPE = /<(path|polygon|polyline|ellipse|circle|rect)\b([^>]*?)\/?>/g

const parseAttributes = (source) => {
  const attributes = {}
  for (const [, name, value] of source.matchAll(/([\w:-]+)\s*=\s*"([^"]*)"/g)) attributes[name] = value
  return attributes
}

/** Every drawn shape in a lockup, minus the full-bleed background rectangle and the text. */
const readShapes = (svg) => {
  const body = svg.replace(/<text[\s\S]*?<\/text>/g, '')
  const shapes = []

  for (const [, tag, rawAttributes] of body.matchAll(SHAPE)) {
    const attributes = parseAttributes(rawAttributes)
    // The artboard-sized rect is the background colour swatch, not part of the mark.
    if (tag === 'rect' && Number(attributes.width) > 3000) continue
    shapes.push({ tag, attributes })
  }

  return shapes
}

/** Exact bounding box across a set of shapes. */
const boundsOf = (shapes) => shapes.reduce((box, { tag, attributes }) => {
  let shapeBox

  if (attributes.d) {
    shapeBox = pathBounds(attributes.d)
  } else if (attributes.points) {
    const numbers = attributes.points.trim().split(/[\s,]+/).map(Number)
    shapeBox = { minX: Infinity, minY: Infinity, maxX: -Infinity, maxY: -Infinity }
    for (let i = 0; i < numbers.length; i += 2) {
      shapeBox.minX = Math.min(shapeBox.minX, numbers[i])
      shapeBox.maxX = Math.max(shapeBox.maxX, numbers[i])
      shapeBox.minY = Math.min(shapeBox.minY, numbers[i + 1])
      shapeBox.maxY = Math.max(shapeBox.maxY, numbers[i + 1])
    }
  } else if (attributes.cx !== undefined) {
    const rx = Number(attributes.rx ?? attributes.r)
    const ry = Number(attributes.ry ?? attributes.r)
    shapeBox = {
      minX: Number(attributes.cx) - rx, maxX: Number(attributes.cx) + rx,
      minY: Number(attributes.cy) - ry, maxY: Number(attributes.cy) + ry
    }
  } else {
    throw new Error(`Cannot measure <${tag}>`)
  }

  return {
    minX: Math.min(box.minX, shapeBox.minX), maxX: Math.max(box.maxX, shapeBox.maxX),
    minY: Math.min(box.minY, shapeBox.minY), maxY: Math.max(box.maxY, shapeBox.maxY)
  }
}, { minX: Infinity, minY: Infinity, maxX: -Infinity, maxY: -Infinity })

/** Re-emits a shape at the origin, stripped of Illustrator's class-based styling. */
const normalizeShape = ({ tag, attributes }, origin) => {
  // Fill is deliberately omitted: it inherits from the wrapping <g>, which is what lets one copy
  // of the mark serve every colourway without any string rewriting at render time.
  const rule = (attributes.class || '').split(/\s+/).includes(EVENODD_CLASS) ? ' fill-rule="evenodd"' : ''

  if (attributes.d) {
    return `<path${rule} d="${translatePath(attributes.d, -origin.x, -origin.y)}"/>`
  }
  if (attributes.points) {
    return `<${tag}${rule} points="${translatePoints(attributes.points, -origin.x, -origin.y)}"/>`
  }
  if (tag === 'ellipse' || tag === 'circle') {
    const cx = round(Number(attributes.cx) - origin.x)
    const cy = round(Number(attributes.cy) - origin.y)
    const radii = attributes.r ? `r="${attributes.r}"` : `rx="${attributes.rx}" ry="${attributes.ry}"`
    return `<${tag} cx="${cx}" cy="${cy}" ${radii}/>`
  }

  throw new Error(`Unhandled shape in the mark: <${tag}>`)
}

const round = (value) => Math.round(value * 100) / 100

// ── Extract each source's mark, normalised to its own origin ─────────────────────────────────────
const extracted = SOURCES.map((file) => {
  const shapes = readShapes(svgOf(file))
  const bounds = boundsOf(shapes)
  const origin = { x: bounds.minX, y: bounds.minY }

  return {
    file,
    bounds,
    shapes,
    markup: shapes.map((shape) => normalizeShape(shape, origin)).join('')
  }
})

function svgOf (file) {
  return readFileSync(resolve(root, 'artwork', file), 'utf8')
}

// ── The consolidation check ──────────────────────────────────────────────────────────────────────
// Compared numerically rather than as strings: the drawings are identical, but each file rounds
// its coordinates against a different artboard offset, so the text never matches exactly.
const [reference, ...rest] = extracted
let worstDelta = 0

for (const candidate of rest) {
  const delta = compare(reference, candidate)
  worstDelta = Math.max(worstDelta, delta)
}

function compare (a, b) {
  const fail = (detail) => {
    console.error(
      `\nThe mark in ${b.file} is not the same drawing as the one in ${a.file}.\n  ${detail}\n\n` +
      'These lockups are meant to embed one shared mark. Re-export them from a single master, or\n' +
      'split the differing artwork into its own asset and give it its own entry in src/assets/.\n'
    )
    process.exit(1)
  }

  if (a.shapes.length !== b.shapes.length) {
    fail(`${a.shapes.length} shapes here, ${b.shapes.length} there.`)
  }

  for (const axis of ['width', 'height']) {
    const sizeA = axis === 'width' ? a.bounds.maxX - a.bounds.minX : a.bounds.maxY - a.bounds.minY
    const sizeB = axis === 'width' ? b.bounds.maxX - b.bounds.minX : b.bounds.maxY - b.bounds.minY
    if (Math.abs(sizeA - sizeB) > COORDINATE_TOLERANCE) {
      fail(`${axis} differs: ${sizeA.toFixed(2)} vs ${sizeB.toFixed(2)} — the marks are not the same size.`)
    }
  }

  let delta = 0

  a.shapes.forEach((shape, index) => {
    const other = b.shapes[index]
    if (shape.tag !== other.tag) fail(`shape ${index} is <${shape.tag}> here and <${other.tag}> there.`)

    const here = numbersOf(shape, a.bounds)
    const there = numbersOf(other, b.bounds)
    if (here.length !== there.length) fail(`shape ${index} has a different number of coordinates.`)

    here.forEach((value, position) => {
      const difference = Math.abs(value - there[position])
      if (difference > COORDINATE_TOLERANCE) {
        fail(`shape ${index}, coordinate ${position}: ${value.toFixed(3)} vs ${there[position].toFixed(3)}.`)
      }
      delta = Math.max(delta, difference)
    })
  })

  return delta
}

// A shape's coordinates in origin-relative space. Path commands are compared alongside their
// numbers so a structural change cannot hide behind coincidentally similar values.
function numbersOf ({ tag, attributes }, bounds) {
  if (attributes.d) {
    const values = []
    for (const { command, values: group } of parsePath(attributes.d)) {
      values.push(command.charCodeAt(0))
      const relative = command !== command.toUpperCase()
      group.forEach((value, index) => {
        // Relative commands are already translation-invariant; absolute ones need the origin
        // subtracted before the two files can be compared in the same space.
        if (relative) values.push(value)
        else values.push(value - (index % 2 === 0 ? bounds.minX : bounds.minY))
      })
    }
    return values
  }

  if (attributes.points) {
    return attributes.points.trim().split(/[\s,]+/)
      .map((value, index) => Number(value) - (index % 2 === 0 ? bounds.minX : bounds.minY))
  }

  return [
    Number(attributes.cx) - bounds.minX,
    Number(attributes.cy) - bounds.minY,
    Number(attributes.rx ?? attributes.r),
    Number(attributes.ry ?? attributes.r)
  ]
}

// ── Emit ─────────────────────────────────────────────────────────────────────────────────────────
const width = round(reference.bounds.maxX - reference.bounds.minX)
const height = round(reference.bounds.maxY - reference.bounds.minY)

writeFileSync(resolve(root, 'src/assets/markup.js'), `// Generated by scripts/build-mark.mjs — do not edit.
//
// The Province of British Columbia mark, extracted from artwork/ and normalised to its own origin.
// All three lockups embed this one drawing; the build script verifies they are identical (to
// within Illustrator's ${COORDINATE_TOLERANCE}-unit coordinate rounding) before writing this file.
//
// Shapes carry no fill of their own — colour inherits from the wrapping <g>, so a single copy
// serves every colourway without rewriting any markup.

export const PROVINCIAL_MARK = {
  viewBox: { width: ${width}, height: ${height} },
  inner: '${reference.markup.replace(/\\/g, '\\\\').replace(/'/g, "\\'")}'
}
`)

const each = reference.markup.length
const shapeCount = reference.shapes.length

console.log(`  mark verified identical across ${SOURCES.length} lockups (largest coordinate delta ${worstDelta.toFixed(3)})`)
console.log(`  ${width} × ${height}, ${shapeCount} shapes, ${(each / 1024).toFixed(1)} KB`)
console.log(`  → src/assets/markup.js (${((SOURCES.length - 1) * each / 1024).toFixed(1)} KB of duplicated path data dropped)`)
