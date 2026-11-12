// Writes <out>/bc-province-current/brand.json: the BC mark (2011 to the present), the Province's
// published mark with each ministry's name beside it.
//
// Two kinds of artwork, kept apart as PofBC keeps them:
//
//   - The published marks, exactly. The Province's guidelines say the marks are used exactly as
//     provided, so the mark is the drawing PofBC lifted unchanged from the published PDF
//     (src/assets/currentMark.js), and every published ministry name is drawn by PofBC's
//     renderer (src/current/currentMarks.js) in the alphabet recovered from the marks themselves,
//     in both languages and all four official colourways, into artwork/ministry-marks/. These are
//     the files to use.
//   - An editable signature, for names no mark has shown. The mark, the gold divider and the name
//     where PofBC's layout puts them: the name's last line on the wordmark's baseline, 8.1 pt
//     leading, growing upward. The Province's serif (Adobe Garamond Pro) is licensed, so the name
//     is set in EB Garamond, an open revival, and does not match the published lettering exactly;
//     the fonts' notice says so.
//
// The wrap is only a backstop (EB Garamond runs wider than the Province's tracked Garamond, so it is
// PofBC's three-line measure, 13000/1000 em): the listed names arrive already broken.
//
// brandkit hangs a stack from its first line, so the name is two stacks: an optional opening line
// ("Ministry of", when the name takes three lines) two leadings above the baseline, and the rest
// (two lines) one leading above it. Each department's values are split by PofBC's own line rules
// (src/current/currentLayout.js nameLines), so the listed ministries break as the Province's do.
//
//   npm run brandkit:build -- bc-province-current

import { mkdirSync, writeFileSync } from 'node:fs'
import { resolve } from 'node:path'
import { pofbc } from '../lib/paths.mjs'
import { folderOf, HEROS, HEROS_FILES, round, writeEraBrand } from '../lib/era.mjs'
import { ministriesBetween } from '../lib/ministries.mjs'

const ID = 'bc-province-current'
const folder = folderOf(ID)
const { CURRENT_MARK, NAME_LEADING } = await pofbc('src/assets/currentMark.js')
const { BCID, CURRENT_VARIANTS, CURRENT_VARIANT_ORDER, renderCurrentSvg } = await pofbc('src/current/currentMarks.js')
const { MINISTRIES } = await pofbc('src/current/ministries.js')
const { nameLines } = await pofbc('src/current/currentLayout.js')

// --- The published marks, drawn by PofBC: <code>-<language>-<colourway>.svg.
const marksFolder = resolve(folder, 'artwork/ministry-marks')
mkdirSync(marksFolder, { recursive: true })
const markFiles = []
const index = []
for (const ministry of MINISTRIES) {
  for (const language of ['en', 'fr']) {
    const text = ministry[language]
    if (!text) continue
    const files = {}
    for (const variant of CURRENT_VARIANT_ORDER) {
      const name = `${ministry.code.toLowerCase()}-${language}-${variant}.svg`
      writeFileSync(resolve(marksFolder, name), renderCurrentSvg({ text, language, variant, title: text.replace(/\n/g, ' ') }))
      markFiles.push(`artwork/ministry-marks/${name}`)
      files[variant] = name
    }
    index.push({ code: ministry.code, language, name: text.replace(/\n/g, ' '), lines: text.includes('\n') ? text.split('\n') : nameLines(text, { language }), files })
  }
}
writeFileSync(resolve(marksFolder, 'index.json'), `${JSON.stringify({ source: 'Drawn by PofBC (src/current/currentMarks.js renderCurrentSvg): the published BC mark, and each name set in the alphabet recovered from the published marks.', colourways: Object.fromEntries(CURRENT_VARIANT_ORDER.map((id) => [id, CURRENT_VARIANTS[id].description])), marks: index }, null, 1)}\n`)
markFiles.push('artwork/ministry-marks/index.json')

// --- The mark as a brand symbol, its parts as roles, in units of 1/100 pt.
//
// Without its knockout: the white disc behind the sun that shows between the rays. brandkit paints
// a one-ink logo (a black symbol file, the brand menu's logo) by giving every role the same
// colour, which would fill the rays in solid; left out, the rays stay open in every ink. On white
// the colour mark looks the same either way; only the Reverse colourway differs, showing the
// ground between the rays rather than white. Its published files (artwork/ministry-marks/
// *-reverse.svg) keep the knockout, as the Province draws it.
const U = 100
const mark = CURRENT_MARK.en
const shapes = (language) => CURRENT_MARK[language].shapes
  .filter((shape) => shape.role !== 'knockout')
  .map((shape) => `<path d="${shape.d}"${shape.rule ? ` fill-rule="${shape.rule}"` : ''} fill="{${shape.role}}"/>`).join('')
const symbolOf = (language, title) => ({
  name: `bc-mark-${language}`,
  title,
  masterTitle: `${title}, as published`,
  masterDescription: 'The Province’s BC mark, lifted unchanged from the published ministry marks: the sun, the mountains and sea, and the wordmark, every shape labelled with its part so the official colourways can paint it.',
  viewBox: [0, 0, CURRENT_MARK[language].width, CURRENT_MARK[language].height],
  markup: shapes(language)
})

const divider = (language) => {
  const d = CURRENT_MARK[language].divider
  return { type: 'art', x: round(d.x * U), y: 0, scale: U, bounds: [0, 0, d.width, d.height], markup: `<rect width="${d.width}" height="${d.height}" fill="{divider}"/>` }
}
const SIZE = round(mark.size * U)
const LEAD = round(NAME_LEADING * U)
const nameStacks = (language) => {
  const m = CURRENT_MARK[language]
  return [
    { type: 'stack', id: 'lead', x: round(m.nameX * U), y: round((m.baseline - 2 * NAME_LEADING) * U), items: [{ field: 'ministry-lead', size: SIZE, font: 'serif', leading: LEAD, role: 'name' }] },
    { type: 'stack', id: 'name', x: round(m.nameX * U), y: round((m.baseline - NAME_LEADING) * U), items: [{ field: 'ministry', size: SIZE, font: 'serif', leading: LEAD, wrap: round(13000 / 1000 * mark.size * U), maxLines: 2, role: 'name' }] }
  ]
}
const SIGNATURES = [
  {
    id: 'mark', label: 'The BC mark', use: 'The mark on its own: the Province as a whole.',
    metrics: { font: 'serif', capHeight: round(mark.size * 0.65 * U), baseline: round(mark.baseline * U), logotypeX: 0 },
    elements: [{ type: 'symbol', x: 0, y: 0, height: round(mark.height * U) }]
  },
  {
    id: 'ministry', label: 'Ministry mark', departmental: true,
    use: 'The mark, the gold divider and the ministry, its last line on the wordmark’s baseline. Use the published file (artwork/ministry-marks) for any listed ministry; this editable form is for names no mark has shown, and sets them in EB Garamond.',
    metrics: { font: 'serif', capHeight: round(mark.size * 0.65 * U), baseline: round(mark.baseline * U), logotypeX: round(mark.nameX * U) },
    elements: [{ type: 'symbol', x: 0, y: 0, height: round(mark.height * U) }, divider('en'), ...nameStacks('en')]
  },
  {
    id: 'ministere', label: 'Ministry mark, French', departmental: true,
    use: 'The French mark (Colombie-Britannique), with the ministry beside it. Use the published file for any listed ministry.',
    metrics: { font: 'serif', capHeight: round(mark.size * 0.65 * U), baseline: round(CURRENT_MARK.fr.baseline * U), logotypeX: round(CURRENT_MARK.fr.nameX * U) },
    elements: [{ type: 'symbol', symbol: 'bc-mark-fr', x: 0, y: 0, height: round(CURRENT_MARK.fr.height * U) }, divider('fr'), ...nameStacks('fr')]
  }
]

// --- Ministries: the published names first (their breaks as published), then every other ministry
// since 2011, broken by PofBC's rules.
const split = (lines) => lines.length > 2 ? { 'ministry-lead': lines[0], ministry: lines.slice(1).join('\n') } : { 'ministry-lead': '', ministry: lines.join('\n') }
const published = MINISTRIES.map((ministry) => {
  const lines = nameLines(ministry.en, { language: 'en' })
  return { id: ministry.code.toLowerCase(), name: ministry.en.replace(/\n/g, ' '), group: 'Published marks', matched: `artwork/ministry-marks/${ministry.code.toLowerCase()}-en-colour.svg`, values: split(lines) }
})
const publishedNames = new Set(published.map((item) => item.name))
const historical = (await ministriesBetween(2011, 9999, { values: (name) => split(nameLines(name, { language: 'en' })) }))
  .filter((item) => !publishedNames.has(item.name))
  .map((item) => ({ ...item, id: `since-2011-${item.id}`, group: 'Other ministries since 2011' }))

const COLOURWAYS = Object.fromEntries(CURRENT_VARIANT_ORDER.map((id) => {
  const fills = CURRENT_VARIANTS[id].fills
  const key = (value) => Object.entries({ blue: BCID.blue, gold: BCID.gold, blueTint: BCID.blueTint, goldTint: BCID.goldTint, white: BCID.white, black: BCID.black }).find(([, hex]) => hex.toLowerCase() === value.toLowerCase())?.[0] ?? value
  return [id, {
    label: CURRENT_VARIANTS[id].label,
    roles: { sun: key(fills.sun), mountains: key(fills.mountains), wordmark: key(fills.wordmark), divider: key(fills.divider), name: key(fills.name), symbol: key(fills.wordmark) },
    ...(id === 'reverse' || id === 'white' ? { ground: 'blue' } : {})
  }]
}))

export const brand = {
  schema: 'brandkit/1',
  id: ID,
  name: 'Province of British Columbia (BC mark)',
  version: 'bc-mark-2011',
  displayVersion: 'BC mark, 2011–present',
  source: 'PofBC’s current era: the BC mark lifted unchanged from the Province’s published ministry-marks PDF (artwork/current/ministry-marks.pdf), the alphabet recovered from those marks, and the colour-accessibility guidance’s four colourways.',
  status: 'A reference kit built from the Province’s published artwork. It is not issued by the Government of British Columbia and is not a source of approved marks: use the Province’s own files for official work.',
  colours: { blue: '#234075', gold: '#E3A82B', blueTint: '#7B8CAC', goldTint: '#EECB80', white: '#FFFFFF', black: '#000000', paper: '#FFFFFF' },
  colourNames: { blue: 'BC Blue', gold: 'BC Gold', blueTint: 'BC Blue 60%', goldTint: 'BC Gold 60%' },
  roles: { ink: 'black', paper: 'paper', muted: '#555555', primary: 'blue', light: 'goldTint', reverse: 'white', line: '#D8D8D8', rule: 'gold', symbol: 'blue', type: 'blue' },
  print: { note: 'The PDF draws the marks in CMYK-native #053673 and #fdb913; the colour-accessibility guidance specifies #234075 and #e3a82b for screen, which are used here.' },
  colourways: COLOURWAYS,
  defaultColourway: 'colour',
  logoColours: ['blue', 'black', 'white', 'currentColor'],
  rasterColours: ['blue', 'black', 'white'],
  fonts: {
    serif: { family: 'EB Garamond', office: 'Adobe Garamond Pro', officialFamily: 'Adobe Garamond Pro', stack: '"EB Garamond", "Adobe Garamond Pro", Garamond, serif', weight: 400, capHeight: 0.65, file: 'fonts/eb-garamond/eb-garamond-latin-400-normal.woff', web: 'fonts/eb-garamond/eb-garamond-latin-400-normal.woff', label: 'Adobe Garamond Pro (EB Garamond stand-in)', note: 'The marks are lettered in Adobe Garamond Pro, kerned and tracked −10/1000 em. EB Garamond is an open revival standing in for it and differs in its letterforms.' },
    serifItalic: { family: 'EB Garamond', stack: '"EB Garamond", Garamond, serif', weight: 400, style: 'italic', capHeight: 0.65, file: 'fonts/eb-garamond/eb-garamond-latin-400-italic.woff', web: 'fonts/eb-garamond/eb-garamond-latin-400-italic.woff', label: 'Garamond Italic (EB Garamond)' },
    serifBold: { family: 'EB Garamond', stack: '"EB Garamond", Garamond, serif', weight: 700, capHeight: 0.65, file: 'fonts/eb-garamond/eb-garamond-latin-700-normal.woff', web: 'fonts/eb-garamond/eb-garamond-latin-700-normal.woff', label: 'Garamond Bold (EB Garamond)' },
    regular: HEROS.regular, bold: HEROS.bold,
    body: HEROS.regular, display: { family: 'EB Garamond', stack: '"EB Garamond", Garamond, serif', weight: 400, capHeight: 0.65, file: 'fonts/eb-garamond/eb-garamond-latin-400-normal.woff', web: 'fonts/eb-garamond/eb-garamond-latin-400-normal.woff', label: 'Garamond (EB Garamond)' },
    displayRegular: HEROS.regular, extra: HEROS.bold, label: HEROS.regular
  },
  typography: {
    headlines: { family: 'EB Garamond', weight: 400, trackingEm: -0.01 },
    body: { family: 'TeX Gyre Heros', weight: 400 },
    labels: { family: 'TeX Gyre Heros', weight: 400, trackingEm: 0.04 },
    note: 'The ministry marks are lettered in Adobe Garamond Pro (EB Garamond here). For screen text the Province uses BC Sans, which this kit does not include; TeX Gyre Heros sets this kit’s own pages.'
  },
  symbol: symbolOf('en', 'The BC mark'),
  symbols: { 'bc-mark-fr': symbolOf('fr', 'La marque BC') },
  signatures: SIGNATURES,
  lockup: { canvasPadding: 0, clearspaceRecommendation: 'Use the marks exactly as provided: never redrawn, recoloured outside the four colourways, or rearranged.', minimumHorizontalWidthPx: 120, minimumHorizontalWidthMm: 25 },
  departments: { label: 'Ministry', field: 'ministry', folder: 'ministries', colourways: ['colour'], items: [...published, ...historical], note: 'The ministries with published marks (their exact artwork is in artwork/ministry-marks), then every other ministry since 2011 in PofBC’s ministry history, broken into lines by PofBC’s rules.' },
  fields: {
    'ministry-lead': { label: 'Opening line (three-line names only)', placeholder: '' },
    ministry: { label: 'Ministry (last two lines)', placeholder: 'Ministry of\nAbcdefghijk', multiline: true }
  },
  copy: {
    svgDescription: 'Province of British Columbia BC mark with a ministry name, from the published artwork, for reference. Not issued by the Government of British Columbia.',
    templateDescription: 'Province of British Columbia, BC mark (2011–present), reference kit. Not issued by the Government of British Columbia.',
    logoLabel: 'Province of British Columbia ministry mark',
    motifLabel: 'The BC mark',
    tagline: 'The mark, exactly as provided.'
  },
  templates: [],
  web: {
    componentName: 'BcMinistryMark',
    symbolComponentName: 'BcMark',
    cssPrefix: 'bcmark',
    appIcon: { background: 'paper', colour: 'primary', size: 860 },
    favicon: { light: '#234075', dark: '#FFFFFF', size: 60, micro: false, title: '{name} favicon' },
    intro: { eyebrow: 'BC mark / 2011–present', headline: 'Province of\nBritish Columbia', body: 'The BC mark as the Province publishes it, with every published ministry mark in both languages and four colourways. A reference kit, not a source of approved marks.', edition: 'BC mark reference kit', footer: 'Province of British Columbia BC mark, from published artwork. Not issued by the Government of British Columbia.' },
    landing: { eyebrow: 'Reference', headline: 'Province of\nBritish Columbia', body: 'The BC mark and the ministry marks.', cta: 'Open the marks', contactEyebrow: 'Official artwork', contactBody: 'For approved marks and guidance, see the Government of British Columbia.', footer: 'BC mark reference kit.' }
  },
  files: [
    { to: 'README.md', from: 'docs/README.md' },
    'fonts/eb-garamond/OFL.txt', 'fonts/eb-garamond/FONT-NOTICE.txt',
    ...['400-normal', '400-italic', '700-normal'].map((cut) => `fonts/eb-garamond/eb-garamond-latin-${cut}.woff`),
    ...markFiles,
    ...HEROS_FILES
  ]
}

writeEraBrand(brand)
