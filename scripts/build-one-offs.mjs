// Lifts the gallery's one-off marks out of the artwork they were published in.
//
// These are the marks of the Best Place on Earth years — WelcomeBC, WorkBC and their like — each a
// BC mark beside a name that follows no ministry pattern. They are kept as drawn, not rebuilt: every
// shape comes out of the published file, and is labelled with the part it plays so the gallery can
// recolour it.
//
// Two things in these files are not plain vector artwork, and both are handled here:
//
//   The sun's glow. The PDF shaded the sun, its rays and its core, and the converter wrote each
//   shading as a small bitmap clipped to the shape it fills. The bitmaps are sampled back into
//   radial gradients about the sun's centre, as a fraction of the way from the core's light to the
//   sun's gold, so the glow survives recolouring and stays vector.
//
//   A mark with no artwork. BC Stats is known only from a screenshot, which shows WorkBC's
//   arrangement with "BCStats" in place of "WorkBC". It is composed from WorkBC's shapes, with the
//   wording typeset on WorkBC's own line — the size, origin, baseline and tracking fitted off
//   WorkBC's drawn letters, and checked by setting "WorkBC" on it and comparing.
//
// Writes src/assets/oneOffMarks.js. Committed: it is the Province's drawing, as the other assets are.
//
// Run: npm run build:one-offs

import { readFileSync, writeFileSync } from 'node:fs'
import { resolve, dirname } from 'node:path'
import { fileURLToPath } from 'node:url'
import { inflateSync } from 'node:zlib'
import published from '../src/current/nameGlyphs.js'
import lifted from '../src/current/liftedGlyphs.js'
import { KERNING, WIDTHS } from '../src/current/nameMetrics.js'
import { absolute, boundsOf } from './svgAbsolute.mjs'
import { fitLine, groupLetters } from './letterFit.mjs'

const root = resolve(dirname(fileURLToPath(import.meta.url)), '..')
const SOURCE = resolve(root, 'artwork/one-offs')
const target = resolve(root, 'src/assets/oneOffMarks.js')
const glyphs = { ...lifted, ...published }

/** Worst disagreement, in 1/1000 em, between a typeset line and the drawn one it stands in for. */
const TOLERANCE = 4

/**
 * Letters whose height is not checked when a line is re-set, only their spacing.
 *
 * The committed W sits 14/1000 em lower than the W drawn in both WelcomeBC and WorkBC, and exactly
 * where the licensed font puts it: it was recovered from the one corrupt file that has a W, and its
 * height looks to have come from the font rather than the artwork. That is a question about the
 * ministry alphabet, not about this line, so it is reported rather than allowed to fail the check.
 */
const HEIGHT_UNCHECKED = new Set(['W'])

// ── Reading the file ─────────────────────────────────────────────────────────────────────────────

const attributesOf = (text) => Object.fromEntries([...text.matchAll(/([\w:-]+)="([^"]*)"/g)].map((m) => [m[1], m[2]]))

/**
 * Every drawn path and image, with the fill it inherits and the clip paths it sits inside.
 * Converters write fills on groups as often as on shapes, so inheritance is followed.
 */
function parse (source) {
  const [, , width, height] = /viewBox="([^"]+)"/.exec(source)[1].split(/\s+/).map(Number)
  const clips = new Map()
  const items = []
  const stack = [{ fill: '#000', clips: [] }]
  let clipId = null

  for (const [, closing, tag, body, selfClosing] of source.matchAll(/<(\/?)([a-zA-Z]+)([^>]*?)(\/?)>/g)) {
    const attrs = attributesOf(body)
    if (tag === 'clipPath') {
      if (closing) clipId = null
      else {
        clips.set(attrs.id, [])
        if (!selfClosing) clipId = attrs.id
      }
      continue
    }
    if (clipId) {
      if (tag === 'path' && attrs.d) clips.get(clipId).push(attrs.d)
      continue
    }
    if (tag === 'g') {
      if (closing) stack.pop()
      else if (!selfClosing) {
        const parent = stack.at(-1)
        stack.push({
          fill: attrs.fill ?? parent.fill,
          clips: attrs['clip-path'] ? [...parent.clips, attrs['clip-path'].slice(5, -1)] : parent.clips
        })
      }
      continue
    }
    if (closing || (tag !== 'path' && tag !== 'image')) continue
    const parent = stack.at(-1)
    items.push({
      tag,
      ...attrs,
      fill: attrs.fill ?? parent.fill,
      clips: attrs['clip-path'] ? [...parent.clips, attrs['clip-path'].slice(5, -1)] : parent.clips
    })
  }

  return { width, height, clips, items }
}

/** A clip is a crop if it is one axis-aligned rectangle, however the converter spelled it. */
function isRectangle (paths) {
  if (paths.length !== 1) return false
  const subpaths = absolute(paths[0])
  if (subpaths.length !== 1) return false
  const points = subpaths[0].filter(([command]) => command !== 'Z')
  if (points.some(([command]) => command === 'C') || points.length > 5) return false
  return points.every(([, x, y], i) => {
    const [, px, py] = points[(i + points.length - 1) % points.length]
    // Converters round each edge separately, so a rectangle can come back 0.001 out of true.
    return Math.abs(x - px) < 0.01 || Math.abs(y - py) < 0.01
  })
}

/** The innermost clip that is a real shape rather than a crop, or null. */
function shapeClip (clips, ids) {
  for (const id of [...ids].reverse()) {
    const paths = clips.get(id) ?? []
    if (!paths.length || isRectangle(paths)) continue
    const subpaths = paths.flatMap(absolute)
    const box = union(subpaths.map(boundsOf))
    if (box.right - box.left < 0.5 || box.bottom - box.top < 0.5) return { degenerate: true }
    return { subpaths, box }
  }
  return null
}

const union = (boxes) => boxes.reduce((a, b) => ({
  left: Math.min(a.left, b.left),
  top: Math.min(a.top, b.top),
  right: Math.max(a.right, b.right),
  bottom: Math.max(a.bottom, b.bottom)
}), { left: Infinity, top: Infinity, right: -Infinity, bottom: -Infinity })

// ── Bitmaps ──────────────────────────────────────────────────────────────────────────────────────

/** An RGBA or RGB PNG as rows of [r, g, b, a]. Only what the converter writes is supported. */
function decodePng (buffer) {
  let offset = 8
  let width, height, type
  const data = []
  while (offset < buffer.length) {
    const length = buffer.readUInt32BE(offset)
    const kind = buffer.toString('ascii', offset + 4, offset + 8)
    const chunk = buffer.subarray(offset + 8, offset + 8 + length)
    if (kind === 'IHDR') { width = chunk.readUInt32BE(0); height = chunk.readUInt32BE(4); type = chunk[9] }
    if (kind === 'IDAT') data.push(chunk)
    offset += 12 + length
  }
  const channels = { 2: 3, 6: 4 }[type]
  if (!channels) return null
  const raw = inflateSync(Buffer.concat(data))
  const stride = width * channels
  const rows = []
  let previous = new Uint8Array(stride)
  for (let y = 0, p = 0; y < height; y += 1) {
    const filter = raw[p++]
    const line = Uint8Array.from(raw.subarray(p, p + stride))
    p += stride
    for (let x = 0; x < stride; x += 1) {
      const a = x >= channels ? line[x - channels] : 0
      const b = previous[x]
      const c = x >= channels ? previous[x - channels] : 0
      const predictor = filter === 1 ? a : filter === 2 ? b : filter === 3 ? (a + b) >> 1
        : filter === 4 ? (() => {
          const guess = a + b - c
          const [da, db, dc] = [Math.abs(guess - a), Math.abs(guess - b), Math.abs(guess - c)]
          return da <= db && da <= dc ? a : db <= dc ? b : c
        })() : 0
      line[x] = (line[x] + predictor) & 255
    }
    rows.push(Array.from({ length: width }, (_, i) => {
      const px = line.subarray(i * channels, i * channels + channels)
      return [px[0], px[1], px[2], channels === 4 ? px[3] : 255]
    }))
    previous = line
  }
  return { width, height, rows }
}

function pixelsOf (image) {
  const match = /^data:image\/png;base64,(.*)$/s.exec(image['xlink:href'] ?? image.href ?? '')
  if (!match) return []
  const bitmap = decodePng(Buffer.from(match[1].replace(/\s/g, ''), 'base64'))
  if (!bitmap) return []
  const [x, y, w, h] = ['x', 'y', 'width', 'height'].map((key) => Number(image[key] ?? 0))
  const out = []
  bitmap.rows.forEach((row, j) => row.forEach(([r, g, b, a], i) => {
    if (a < 250) return
    out.push({ x: x + (i + 0.5) * w / bitmap.width, y: y + (j + 0.5) * h / bitmap.height, rgb: [r, g, b] })
  }))
  return out
}

const hex = (rgb) => '#' + rgb.map((v) => Math.round(v).toString(16).padStart(2, '0')).join('')
const rgbOf = (colour) => [1, 3, 5].map((i) => parseInt(colour.slice(i, i + 2), 16))
const isGold = ([r, g, b]) => r > 200 && g > 140 && b < 90
const isRed = ([r, g, b]) => r > 150 && r > g + 70 && r > b + 70

/**
 * A shading sampled back into gradient stops about the sun's centre.
 *
 * Each pixel becomes a distance from the centre, as a fraction of the sun's radius, and a mix: how
 * far its colour sits from the core's white toward the sun's gold. Averaged in bands of distance,
 * those are the stops. The spread inside each band is reported, as a check that the shading really
 * was radial about that centre.
 */
function gradientOf (pixels, sun, gold) {
  const white = [255, 255, 255]
  const axis = gold.map((v, i) => v - white[i])
  const length = axis.reduce((sum, v) => sum + v * v, 0)
  const BAND = 0.04
  const bands = new Map()
  for (const { x, y, rgb } of pixels) {
    const distance = Math.hypot(x - sun.cx, y - sun.cy) / sun.r
    const mix = Math.min(1, Math.max(0, rgb.reduce((sum, v, i) => sum + (v - white[i]) * axis[i], 0) / length))
    const band = Math.round(distance / BAND)
    if (!bands.has(band)) bands.set(band, [])
    bands.get(band).push(mix)
  }
  let spread = 0
  const stops = [...bands.entries()].sort(([a], [b]) => a - b).map(([band, mixes]) => {
    const mean = mixes.reduce((a, b) => a + b, 0) / mixes.length
    spread = Math.max(spread, Math.sqrt(mixes.reduce((sum, m) => sum + (m - mean) ** 2, 0) / mixes.length))
    return [Math.round(band * BAND * 1000) / 1000, Math.round(mean * 1000) / 1000]
  })
  return { stops, spread }
}

// ── Classifying the shapes ───────────────────────────────────────────────────────────────────────

function extract (entry) {
  const { width, height, clips, items } = parse(readFileSync(resolve(SOURCE, entry.file), 'utf8'))
  // A mark cut from a whole page names the box it occupies; anything not wholly inside is the page.
  const inside = entry.crop
    ? (box) => box.left >= entry.crop[0] && box.top >= entry.crop[1] && box.right <= entry.crop[2] && box.bottom <= entry.crop[3]
    : (box) => box.right > 0 && box.left < width && box.bottom > 0 && box.top < height
  const covers = (box) => box.left <= 0.5 && box.top <= 0.5 && box.right >= width - 0.5 && box.bottom >= height - 0.5

  // The sun, and anything else the converter drew as a bitmap inside a shape.
  const shaded = []
  for (const image of items.filter((item) => item.tag === 'image')) {
    const clip = shapeClip(clips, image.clips)
    if (!clip || clip.degenerate || !inside(clip.box)) continue
    const pixels = pixelsOf(image)
    if (!pixels.length) continue
    const mean = [0, 1, 2].map((c) => pixels.reduce((sum, p) => sum + p.rgb[c], 0) / pixels.length)
    shaded.push({ ...clip, pixels, mean })
  }
  const leaves = shaded.filter(({ mean }) => isRed(mean))
  const sunParts = shaded.filter((part) => !leaves.includes(part)).sort((a, b) => (b.box.right - b.box.left) - (a.box.right - a.box.left))
  const [disc, second, ...others] = sunParts
  const discWidth = disc.box.right - disc.box.left
  // The core is the broad glow over the sun's middle; everything narrower is a ray.
  const core = second && (second.box.right - second.box.left) > 0.4 * discWidth ? second : null
  const rays = core ? others : [second, ...others].filter(Boolean)
  const sun = { cx: (disc.box.left + disc.box.right) / 2, r: discWidth / 2 }
  sun.cy = disc.box.top + sun.r

  // Everything else is flat colour, taken subpath by subpath.
  const contours = []
  let background = entry.background ?? null
  for (const item of items.filter((i) => i.tag === 'path' && i.d && i.fill !== 'none')) {
    // A flat fill under a shading is the shading's fallback, already covered by the gradient.
    if (shapeClip(clips, item.clips)) continue
    for (const subpath of absolute(item.d)) {
      const box = boundsOf(subpath)
      if (covers(box)) { background ??= item.fill; background = entry.background ?? item.fill; continue }
      if (!inside(box)) continue
      contours.push({ subpath, box, fill: item.fill })
    }
  }

  const gold = (fill) => fill && fill.startsWith('#') && fill.length === 7 && isGold(rgbOf(fill))
  const thin = (box, along) => along === 'x'
    ? box.bottom - box.top > 15 && box.right - box.left < 1.5
    : box.right - box.left > 10 && box.bottom - box.top < 1.5
  const divider = contours.find((c) => gold(c.fill) && thin(c.box, 'x'))
  const rule = contours.find((c) => gold(c.fill) && thin(c.box, 'y') && (!divider || c.box.right < divider.box.left))

  const roles = new Map()
  const add = (role, contour) => {
    if (!roles.has(role)) roles.set(role, { fill: contour.fill, subpaths: [], box: null })
    roles.get(role).subpaths.push(contour.subpath)
  }
  for (const contour of contours) {
    if (contour === divider) add('divider', contour)
    else if (contour === rule) add('rule', contour)
    else if (divider && contour.box.left > divider.box.right) add(gold(contour.fill) ? 'accent' : 'name', contour)
    else if (contour.box.top < sun.cy) add('mountains', contour)
    else if (rule && contour.box.top > rule.box.bottom) add('tagline', contour)
    else add('wordmark', contour)
  }

  const goldOf = hex(disc.pixels.reduce((best, p) => {
    const distance = (rgb) => rgb.reduce((sum, v) => sum + (255 - v) ** 2, 0)
    return distance(p.rgb) > distance(best) ? p.rgb : best
  }, [255, 255, 255]))
  const goldRgb = rgbOf(goldOf)

  const discGradient = gradientOf(disc.pixels, sun, goldRgb)
  const rayGradient = gradientOf(rays.flatMap((ray) => ray.pixels), sun, goldRgb)
  const coreGradient = core ? gradientOf(core.pixels, sun, goldRgb) : null

  const shapes = [
    { role: 'sun', subpaths: disc.subpaths },
    { role: 'rays', subpaths: rays.flatMap((ray) => ray.subpaths) },
    ...(core ? [{ role: 'core', subpaths: core.subpaths }] : []),
    ...['mountains', 'wordmark', 'rule', 'tagline', 'divider', 'name', 'accent']
      .filter((role) => roles.has(role))
      .map((role) => ({ role, subpaths: roles.get(role).subpaths })),
    ...(leaves.length ? [{ role: 'leaf', subpaths: leaves.flatMap((leaf) => leaf.subpaths) }] : [])
  ]

  const colours = {
    background: background ?? null,
    sun: goldOf,
    light: '#ffffff',
    ...Object.fromEntries([...roles].map(([role, { fill }]) => [role, fill])),
    ...(leaves.length ? { leaf: hex(leaves[0].mean) } : {})
  }

  return {
    shapes,
    sun,
    gradients: { sun: discGradient, rays: rayGradient, ...(coreGradient ? { core: coreGradient } : {}) },
    colours,
    roles
  }
}

// ── Typesetting on a drawn line ──────────────────────────────────────────────────────────────────

/** Fits the size, origin and baseline of a mark's drawn wording. */
function lineOf (entry, extracted) {
  const text = entry.wording.map((part) => part.text).join('')
  const contours = ['name', 'accent']
    .flatMap((role) => extracted.roles.get(role)?.subpaths ?? [])
    .map((subpath) => ({ subpath, box: boundsOf(subpath) }))
  const letters = groupLetters(contours)
  const skip = new Set(entry.respaced ?? [])
  return fitLine({
    text, letters, tracking: entry.tracking, isReference: (character) => Boolean(glyphs[character]) && !skip.has(character)
  })
}

/** Wording set as subpaths in the mark's own coordinates, one list per role. */
function typeset (wording, line, tracking) {
  const text = wording.map((part) => part.text).join('')
  const roleAt = wording.flatMap((part) => [...part.text].map(() => part.role))
  const byRole = new Map()
  let pen = 0
  ;[...text].forEach((character, index) => {
    const d = glyphs[character]
    if (!d) throw new Error(`no letterform for ${character}`)
    const scale = line.size / 1000
    const x = line.origin + pen * scale
    const subpaths = absolute(d).map((subpath) => subpath.map(([command, ...v]) =>
      [command, ...v.map((value, i) => (i % 2 === 0 ? x + value * scale : line.baseline + value * scale))]))
    const role = roleAt[index]
    if (!byRole.has(role)) byRole.set(role, [])
    byRole.get(role).push(...subpaths)
    pen += WIDTHS[character]
    const next = text[index + 1]
    if (next !== undefined) pen += tracking + (KERNING[character + next] ?? 0)
  })
  return byRole
}

// ── Build ────────────────────────────────────────────────────────────────────────────────────────

const round = (value) => {
  const text = String(Math.round(value * 100) / 100).replace(/^(-?)0\./, '$1.')
  return text === '-0' ? '0' : text
}

const serialise = (subpaths, dx, dy) => subpaths.map((subpath) => subpath.map(([command, ...v]) =>
  command + v.map((value, i) => round(i % 2 === 0 ? value + dx : value + dy)).join(' ')).join('')).join('').replace(/ -/g, '-')

const manifest = JSON.parse(readFileSync(resolve(SOURCE, 'index.json'), 'utf8'))
const extracted = new Map()
const marks = {}

for (const entry of manifest) {
  let mark
  if (entry.composedFrom) {
    const base = extracted.get(entry.composedFrom)
    const baseEntry = manifest.find((e) => e.id === entry.composedFrom)
    const line = lineOf(baseEntry, base)

    // The check that typesetting on this line reproduces what was drawn on it: the base mark's own
    // wording, set by the same code, against its drawn letters.
    const redrawn = typeset(baseEntry.wording, line, baseEntry.tracking)
    const drawnLetters = groupLetters(['name', 'accent'].flatMap((role) => base.roles.get(role).subpaths)
      .map((subpath) => ({ subpath, box: boundsOf(subpath) })))
    const setLetters = groupLetters([...redrawn.values()].flat().map((subpath) => ({ subpath, box: boundsOf(subpath) })))
    const skip = new Set(baseEntry.respaced ?? [])
    const text = baseEntry.wording.map((part) => part.text).join('')
    const worst = Math.max(...[...text].map((character, i) => skip.has(character) ? 0 : Math.max(
      Math.abs(drawnLetters[i].box.left - setLetters[i].box.left),
      Math.abs(drawnLetters[i].box.right - setLetters[i].box.right),
      HEIGHT_UNCHECKED.has(character) ? 0 : Math.abs(drawnLetters[i].box.bottom - setLetters[i].box.bottom)
    ))) * 1000 / line.size
    if (worst > TOLERANCE) throw new Error(`${entry.id}: "${text}" reset on its own line misses by ${worst.toFixed(1)}/1000 em`)
    console.log(`  ${entry.id.padEnd(20)} "${text}" reset on its line: worst ${worst.toFixed(1)}/1000 em`)

    const wording = typeset(entry.wording, line, entry.tracking)
    mark = {
      ...base,
      shapes: [
        ...base.shapes.filter(({ role }) => role !== 'name' && role !== 'accent'),
        ...['name', 'accent'].filter((role) => wording.has(role)).map((role) => ({ role, subpaths: wording.get(role) }))
      ],
      colours: { ...base.colours, ...entry.colours }
    }
  } else {
    mark = extract(entry)
    extracted.set(entry.id, mark)
  }

  // Onto the mark's own origin: the box of everything drawn.
  const box = union(mark.shapes.flatMap(({ subpaths }) => subpaths.map(boundsOf)))
  const dx = -box.left
  const dy = -box.top
  marks[entry.id] = {
    width: Number(round(box.right - box.left)),
    height: Number(round(box.bottom - box.top)),
    sun: { cx: Number(round(mark.sun.cx + dx)), cy: Number(round(mark.sun.cy + dy)), r: Number(round(mark.sun.r)) },
    gradients: Object.fromEntries(Object.entries(mark.gradients).map(([key, { stops }]) => [key, stops])),
    // Written out in full: #fff is valid SVG, but a colour input only takes six digits.
    printed: Object.fromEntries(Object.entries(mark.colours).map(([role, colour]) => [role,
      /^#[0-9a-f]{3}$/i.test(colour ?? '') ? '#' + [...colour.slice(1)].map((c) => c + c).join('') : colour])),
    shapes: mark.shapes.map(({ role, subpaths }) => ({ role, d: serialise(subpaths, dx, dy) }))
  }

  const spreads = Object.entries(mark.gradients).map(([key, { spread }]) => `${key} ±${spread.toFixed(2)}`).join(', ')
  console.log(`  ${entry.id.padEnd(20)} ${marks[entry.id].width} × ${marks[entry.id].height}, ` +
    `${mark.shapes.map(({ role }) => role).join(' ')}; glow ${spreads}`)
}

writeFileSync(target, `// Generated by scripts/build-one-offs.mjs — do not edit.
//
// The gallery's one-off marks, lifted from the artwork in artwork/one-offs/. Coordinates are in
// points from each mark's own top-left corner. Every shape carries the part it plays, so a mark
// can be recoloured without being redrawn.
//
// \`sun\` is the centre and radius the glow is measured from. \`gradients\` holds its shading as
// [distance, mix] stops: distance from the centre as a fraction of the radius, and how far the
// colour sits from the core's light toward the sun's gold. \`printed\` is the colours as published.

export const ONE_OFF_MARKS = ${JSON.stringify(marks, null, 2)}
`)

console.log('  → src/assets/oneOffMarks.js')
