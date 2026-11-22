// Packages the Crown corporations' and agencies' marks — ICBC, BCLC, BC Ferries, WorkSafeBC, BC
// Transit and BC Parks, and the Department of Recreation and Conservation's of 1970–1973 — from the
// research packages' SVGs, drawn as supplied.
//
// Unlike the one-offs these are not lifted into parts: each file is already one mark, tightly
// cropped, and each says in its own <title> and <desc> what it is — a supplied vector, a declared
// recolour, or a reconstruction. So the drawing is kept exactly as it is, and only what would stop
// it sitting inline on a page is changed: the XML prologue, the title and description (kept as
// data instead), and the ids. Several marks share a page, and two of BCLC's files use the same
// clip ids, so every id a file refers to is prefixed with its mark's key, and the rest — labels
// for the research package's editors, which nothing points at — are dropped.
//
// Writes src/assets/crownMarks.js. Committed: it is the supplied drawing, as the other assets are.
//
// Run: npm run build:crown-marks

import { readFileSync, writeFileSync } from 'node:fs'
import { resolve, dirname } from 'node:path'
import { fileURLToPath } from 'node:url'

const root = resolve(dirname(fileURLToPath(import.meta.url)), '..')
const target = resolve(root, 'src/assets/crownMarks.js')

/** Each mark by the key the gallery knows it by, and the file it is in. */
const MARKS = {
  'icbc-1974-emblem': 'artwork/icbc/00-1974-emblem-linework-reconstructed.svg',
  'icbc-half-disc': 'artwork/icbc/01a-legacy-emblem-reconstructed.svg',
  'icbc-half-disc-lockup': 'artwork/icbc/01b-legacy-icbc-lockup-reconstructed.svg',
  'icbc-full-name': 'artwork/icbc/01-legacy-full-name-reconstructed.svg',
  'icbc-serif-road': 'artwork/icbc/02-serif-road-reconstructed.svg',
  'icbc-square-sans': 'artwork/icbc/03-square-sans-source-cleaned.svg',
  'icbc-rounded-blue': 'artwork/icbc/04-rounded-blue-derived.svg',
  'icbc-rounded-orange': 'artwork/icbc/04-rounded-orange-source-cleaned.svg',
  'icbc-rounded-black': 'artwork/icbc/04-rounded-black-derived.svg',
  'bclc-legacy': 'artwork/bclc/bclc-legacy-monochrome.svg',
  'bclc-legacy-reversed': 'artwork/bclc/bclc-legacy-reversed.svg',
  'bclc-legacy-symbol': 'artwork/bclc/bclc-legacy-symbol.svg',
  'bclc-2008': 'artwork/bclc/bclc-2008-family-palette-reconstruction.svg',
  'bclc-contemporary': 'artwork/bclc/bclc-contemporary-supplied.svg',
  'bcf-toll-condensed': 'artwork/bc-ferries/toll-authority/01-horizontal-condensed-black.svg',
  'bcf-toll-condensed-white': 'artwork/bc-ferries/toll-authority/01-horizontal-condensed-white.svg',
  'bcf-toll-stacked': 'artwork/bc-ferries/toll-authority/02-stacked-bold-black.svg',
  'bcf-toll-stacked-white': 'artwork/bc-ferries/toll-authority/02-stacked-bold-white.svg',
  'bcf-toll-regular': 'artwork/bc-ferries/toll-authority/03-horizontal-regular-black.svg',
  'bcf-toll-regular-white': 'artwork/bc-ferries/toll-authority/03-horizontal-regular-white.svg',
  'bcf-1963-flag': 'artwork/bc-ferries/1963-dogwood-flag-interpretation.svg',
  'bcf-dogwood-lockup': 'artwork/bc-ferries/legacy-lockup-reconstruction.svg',
  'bcf-dogwood-flag': 'artwork/bc-ferries/legacy-geometric-flag.svg',
  'bcf-dogwood-wordmark': 'artwork/bc-ferries/legacy-wordmark-reconstruction.svg',
  'bcf-wave': 'artwork/bc-ferries/current-blue.svg',
  'bcf-wave-white': 'artwork/bc-ferries/current-white.svg',
  'wcb-1983': 'artwork/worksafebc/wcb-1983-family-reconstruction.svg',
  'wcb-1983-symbol': 'artwork/worksafebc/wcb-1983-symbol-reconstruction.svg',
  'worksafebc': 'artwork/worksafebc/worksafebc-current-reconstruction.svg',
  'bct-double-arrow-paper-model': 'artwork/bc-transit/bc-transit-double-arrow-paper-model.svg',
  'bct-flag': 'artwork/bc-transit/bc-transit-flag-on-grey.svg',
  'bct-flag-white': 'artwork/bc-transit/bc-transit-flag.svg',
  'bct-loop-colour': 'artwork/bc-transit/bc-transit-loop-colour-flat.svg',
  'bct-loop-navy': 'artwork/bc-transit/bc-transit-loop-navy.svg',
  'bcp-2023': 'artwork/bc-parks/bc-parks-2023-on-navy.svg',
  'bcp-2023-white': 'artwork/bc-parks/bc-parks-2023.svg',
  'bcp-2023-vertical': 'artwork/bc-parks/bc-parks-2023-vertical-on-navy.svg',
  'bcp-2023-vertical-white': 'artwork/bc-parks/bc-parks-2023-vertical.svg',
  // The Department of Recreation and Conservation's five square symbols (1971–1973), each in black,
  // the reports' two greens and white, and the department's other emblems of 1970 and 1973.
  'drc-department': 'artwork/recreation-conservation/symbols/01_Department_Recreation_Conservation_black.svg',
  'drc-department-green': 'artwork/recreation-conservation/symbols/01_Department_Recreation_Conservation_report_green.svg',
  'drc-department-pale': 'artwork/recreation-conservation/symbols/01_Department_Recreation_Conservation_report_pale.svg',
  'drc-department-white': 'artwork/recreation-conservation/symbols/01_Department_Recreation_Conservation_White.svg',
  'drc-fish-wildlife': 'artwork/recreation-conservation/symbols/02_Fish_and_Wildlife_black.svg',
  'drc-fish-wildlife-green': 'artwork/recreation-conservation/symbols/02_Fish_and_Wildlife_report_green.svg',
  'drc-fish-wildlife-pale': 'artwork/recreation-conservation/symbols/02_Fish_and_Wildlife_report_pale.svg',
  'drc-fish-wildlife-white': 'artwork/recreation-conservation/symbols/02_Fish_and_Wildlife_White.svg',
  'drc-parks': 'artwork/recreation-conservation/symbols/03_Provincial_Parks_black.svg',
  'drc-parks-green': 'artwork/recreation-conservation/symbols/03_Provincial_Parks_report_green.svg',
  'drc-parks-pale': 'artwork/recreation-conservation/symbols/03_Provincial_Parks_report_pale.svg',
  'drc-parks-white': 'artwork/recreation-conservation/symbols/03_Provincial_Parks_White.svg',
  'drc-museum': 'artwork/recreation-conservation/symbols/04_BC_Provincial_Museum_black.svg',
  'drc-museum-green': 'artwork/recreation-conservation/symbols/04_BC_Provincial_Museum_report_green.svg',
  'drc-museum-pale': 'artwork/recreation-conservation/symbols/04_BC_Provincial_Museum_report_pale.svg',
  'drc-museum-white': 'artwork/recreation-conservation/symbols/04_BC_Provincial_Museum_White.svg',
  'drc-fisheries': 'artwork/recreation-conservation/symbols/05_Commercial_Fisheries_Marine_Resources_black.svg',
  'drc-fisheries-green': 'artwork/recreation-conservation/symbols/05_Commercial_Fisheries_Marine_Resources_report_green.svg',
  'drc-fisheries-pale': 'artwork/recreation-conservation/symbols/05_Commercial_Fisheries_Marine_Resources_report_pale.svg',
  'drc-fisheries-white': 'artwork/recreation-conservation/symbols/05_Commercial_Fisheries_Marine_Resources_White.svg',
  'drc-dogwood-oval-1970': 'artwork/recreation-conservation/related_emblems/09_Department_Dogwood_Oval_1970.svg',
  'drc-fw-oval-1973': 'artwork/recreation-conservation/related_emblems/06_Fish_Wildlife_Oval_1973.svg',
  'drc-fw-lockup-1973': 'artwork/recreation-conservation/related_emblems/07_Fish_Wildlife_Paired_Lockup_1973.svg',
  'drc-parks-shield-1973': 'artwork/recreation-conservation/related_emblems/08_Parks_Dogwood_Shield_1973.svg'
}

/** Attributes on the root that its children inherit, and so must survive it being replaced. */
const INHERITED = ['fill', 'fill-rule', 'stroke', 'stroke-width', 'stroke-linejoin', 'stroke-linecap', 'clip-rule']

const attributesOf = (text) => Object.fromEntries([...text.matchAll(/([\w:-]+)="([^"]*)"/g)].map((m) => [m[1], m[2]]))

const decode = (text) => text.replace(/&lt;/g, '<').replace(/&gt;/g, '>').replace(/&quot;/g, '"').replace(/&amp;/g, '&').trim()

const textOf = (source, tag) => {
  const found = source.match(new RegExp(`<${tag}\\b[^>]*>([\\s\\S]*?)</${tag}>`))
  return found ? decode(found[1]).replace(/\s+/g, ' ') : null
}

/** The whole element with this id — its opening tag to its matching close — or null. */
const elementById = (body, id) => {
  const open = new RegExp(`<([\\w:-]+)\\b[^>]*\\sid="${id.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}"[^>]*?(/?)>`).exec(body)
  if (!open) return null
  if (open[2]) return open[0]
  const tag = new RegExp(`<(/?)${open[1]}\\b[^>]*?(/?)>`, 'g')
  tag.lastIndex = open.index + open[0].length
  for (let depth = 1, found; (found = tag.exec(body));) {
    if (found[1]) depth -= 1
    else if (!found[2]) depth += 1
    if (depth === 0) return body.slice(open.index, found.index + found[0].length)
  }
  throw new Error(`#${id} is never closed`)
}

/**
 * A <use> drawn out in full: the element it points at, copied in its place under the <use>'s own
 * position and transform. The copy's ids are dropped, since they would now appear twice; a copy
 * that something else points into cannot be made this way, and is refused. The <defs> the
 * originals sat in are dropped once nothing points into them.
 */
const inlineUses = (body, path) => {
  const inlined = body.replace(/<use\b([^>]*?)\/?>(?:<\/use>)?/g, (_, attributes) => {
    const { id, href, 'xlink:href': xlink, x = 0, y = 0, transform, width, height, ...rest } = attributesOf(attributes)
    const target = (href ?? xlink ?? '').replace(/^#/, '')
    const element = target && elementById(body, target)
    if (!element) throw new Error(`${path}: <use> of #${target}, which it lacks`)
    const copy = element.replace(/\sid="[^"]*"/g, '')
    if (/url\(#/.test(copy)) throw new Error(`${path}: #${target} points elsewhere, so cannot be copied`)
    const place = [Number(x) || Number(y) ? `translate(${Number(x)} ${Number(y)})` : '', transform ?? ''].filter(Boolean).join(' ')
    const kept = Object.entries(rest).map(([name, value]) => ` ${name}="${value}"`).join('')
    return `<g${place ? ` transform="${place}"` : ''}${kept}>${copy}</g>`
  })
  const pointed = new Set([...inlined.matchAll(/url\(#([^)]+)\)|href="#([^"]+)"/g)].map((m) => m[1] ?? m[2]))
  return inlined.replace(/<defs\b[^>]*>[\s\S]*?<\/defs>/g, (defs) =>
    [...defs.matchAll(/\sid="([^"]*)"/g)].some(([, id]) => pointed.has(id)) ? defs : '')
}

const pack = (key, path) => {
  const source = readFileSync(resolve(root, path), 'utf8')
  const svg = source.match(/<svg\b([^>]*)>([\s\S]*)<\/svg>\s*$/)
  if (!svg) throw new Error(`${path}: no <svg> element`)
  const rootAttributes = attributesOf(svg[1])
  const viewBox = (rootAttributes.viewBox ?? `0 0 ${parseFloat(rootAttributes.width)} ${parseFloat(rootAttributes.height)}`)
    .trim().split(/[\s,]+/).map(Number)
  if (viewBox.length !== 4 || viewBox.some((value) => !Number.isFinite(value))) throw new Error(`${path}: no usable viewBox`)

  let body = svg[2]
    .replace(/<!--[\s\S]*?-->/g, '')
    .replace(/<(title|desc|metadata)\b[^>]*>[\s\S]*?<\/\1>/g, '')
  // A shape drawn more than once by <use> (the Fisheries symbol's three fish) is written out, so the
  // mark draws the same with nothing outside it to point at.
  if (/<use\b/.test(body)) body = inlineUses(body, path)

  for (const banned of ['image', 'text', 'script', 'style', 'foreignObject', 'use']) {
    if (new RegExp(`<${banned}\\b`).test(body)) throw new Error(`${path}: has a <${banned}>, which a supplied mark here must not`)
  }

  // Prefix the ids something points at; drop the ones nothing does.
  const referenced = new Set([...body.matchAll(/url\(#([^)]+)\)|href="#([^"]+)"/g)].map((m) => m[1] ?? m[2]))
  body = body
    .replace(/\s(?:inkscape|sodipodi):[\w-]+="[^"]*"/g, '')
    .replace(/\sid="([^"]*)"/g, (_, id) => (referenced.has(id) ? ` id="${key}-${id}"` : ''))
    .replace(/url\(#([^)]+)\)/g, (_, id) => `url(#${key}-${id})`)
    .replace(/>\s+</g, '><')
    .trim()

  const inherited = INHERITED.filter((name) => rootAttributes[name] !== undefined)
    .map((name) => ` ${name}="${rootAttributes[name]}"`).join('')
  if (inherited) body = `<g${inherited}>${body}</g>`

  const inks = [...new Set([...body.matchAll(/(?:fill|stroke)="(#[0-9a-fA-F]{3,6})"/g)].map((m) => m[1].toLowerCase()))]

  return { source: path, title: textOf(source, 'title'), description: textOf(source, 'desc'), viewBox, inks, body }
}

const marks = Object.fromEntries(Object.entries(MARKS).map(([key, path]) => [key, pack(key, path)]))

const header = `// Generated by scripts/build-crown-marks.mjs — do not edit.
//
// ICBC's, BCLC's, BC Ferries', WorkSafeBC's, BC Transit's, BC Parks' and the Department of Recreation
// and Conservation's marks, from the research packages in
// research/identity/, drawn exactly as supplied. \`body\` is each file's drawing with its ids
// prefixed by the mark's key; \`title\` and \`description\` are the file's own account of what it is;
// \`inks\` are the colours it uses.

export const CROWN_MARKS = {
${Object.entries(marks).map(([key, mark]) => `  ${JSON.stringify(key)}: ${JSON.stringify(mark)}`).join(',\n')}
}
`

writeFileSync(target, header)
console.log(`Wrote ${Object.keys(marks).length} marks to ${target}`)
