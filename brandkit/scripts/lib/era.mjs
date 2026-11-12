// Shared pieces of the era brands written in this repository (engraved arms, flag, arms, current):
// TeX Gyre Heros standing in for Helvetica, and the closing step every generator takes.

import { readFileSync, writeFileSync } from 'node:fs'
import { fileURLToPath } from 'node:url'
import { brandFolder } from './paths.mjs'
import { updateManifest } from './common.mjs'

const TEX_GYRE = ['GUST-FONT-LICENSE.txt', 'FONT-NOTICE.txt', 'texgyreheros-regular.otf', 'texgyreheros-bold.otf', 'texgyreheros-italic.otf', 'texgyreheros-bolditalic.otf']

/** TeX Gyre Heros as a brandkit face: Helvetica's widths, under the GUST licence. Word asks for Helvetica. */
export const heros = (file, label, extra = {}) => ({
  family: 'TeX Gyre Heros', office: 'Helvetica', officialFamily: 'Helvetica',
  stack: '"TeX Gyre Heros", Helvetica, Arial, sans-serif', weight: 400, capHeight: 0.729,
  file: `fonts/${file}`, web: `fonts/${file}`, label, ...extra
})
export const HEROS = {
  regular: heros('texgyreheros-regular.otf', 'Helvetica Regular (TeX Gyre Heros)'),
  bold: heros('texgyreheros-bold.otf', 'Helvetica Bold (TeX Gyre Heros Bold)', { weight: 700 }),
  italic: heros('texgyreheros-italic.otf', 'Helvetica Italic (TeX Gyre Heros Italic)', { style: 'italic' })
}
export const HEROS_FILES = TEX_GYRE.map((name) => `fonts/${name}`)

/** The folder an era writes into, as a path. */
export const folderOf = (id) => fileURLToPath(brandFolder(id))

/** Writes brand.json and keeps <out>/index.json in step. */
export const writeEraBrand = (brand) => {
  const url = new URL('brand.json', brandFolder(brand.id))
  writeFileSync(url, `${JSON.stringify(brand, null, 1)}\n`)
  updateManifest(brand)
  console.log(`${brand.id}: ${brand.templates?.length ?? 0} templates, ${brand.signatures?.length ?? 0} signatures, ${brand.departments?.items?.length ?? 0} ${brand.departments?.label?.toLowerCase() ?? 'department'} entries`)
}

/** An SVG file's inner markup and viewBox. */
export const readSvg = (path) => {
  const source = readFileSync(path, 'utf8')
  const viewBox = /viewBox="([^"]+)"/.exec(source)[1].split(/[\s,]+/).map(Number)
  const inner = source.replace(/^[\s\S]*?<svg[^>]*>/, '').replace(/<\/svg>\s*$/, '').replace(/<title>[\s\S]*?<\/title>|<desc>[\s\S]*?<\/desc>/g, '').trim()
  return { viewBox, inner }
}

export const round = (value, places = 3) => Math.round(value * 10 ** places) / 10 ** places
