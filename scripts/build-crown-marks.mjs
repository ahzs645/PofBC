// Packages ICBC's, BCLC's, BC Ferries' and WorkSafeBC's marks from the research packages' SVGs, drawn as supplied.
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
  'bcf-1963-flag': 'artwork/bc-ferries/1963-dogwood-flag-interpretation.svg',
  'bcf-dogwood-lockup': 'artwork/bc-ferries/legacy-lockup-reconstruction.svg',
  'bcf-dogwood-flag': 'artwork/bc-ferries/legacy-geometric-flag.svg',
  'bcf-dogwood-wordmark': 'artwork/bc-ferries/legacy-wordmark-reconstruction.svg',
  'bcf-wave': 'artwork/bc-ferries/current-blue.svg',
  'bcf-wave-white': 'artwork/bc-ferries/current-white.svg',
  'wcb-1983': 'artwork/worksafebc/wcb-1983-family-reconstruction.svg',
  'wcb-1983-symbol': 'artwork/worksafebc/wcb-1983-symbol-reconstruction.svg',
  'worksafebc': 'artwork/worksafebc/worksafebc-current-reconstruction.svg'
}

/** Attributes on the root that its children inherit, and so must survive it being replaced. */
const INHERITED = ['fill', 'fill-rule', 'stroke', 'stroke-width', 'stroke-linejoin', 'stroke-linecap', 'clip-rule']

const attributesOf = (text) => Object.fromEntries([...text.matchAll(/([\w:-]+)="([^"]*)"/g)].map((m) => [m[1], m[2]]))

const decode = (text) => text.replace(/&lt;/g, '<').replace(/&gt;/g, '>').replace(/&quot;/g, '"').replace(/&amp;/g, '&').trim()

const textOf = (source, tag) => {
  const found = source.match(new RegExp(`<${tag}\\b[^>]*>([\\s\\S]*?)</${tag}>`))
  return found ? decode(found[1]).replace(/\s+/g, ' ') : null
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
// ICBC's, BCLC's, BC Ferries' and WorkSafeBC's marks, from the research packages in
// research/identity/, drawn exactly as supplied. \`body\` is each file's drawing with its ids
// prefixed by the mark's key; \`title\` and \`description\` are the file's own account of what it is;
// \`inks\` are the colours it uses.

export const CROWN_MARKS = {
${Object.entries(marks).map(([key, mark]) => `  ${JSON.stringify(key)}: ${JSON.stringify(mark)}`).join(',\n')}
}
`

writeFileSync(target, header)
console.log(`Wrote ${Object.keys(marks).length} marks to ${target}`)
