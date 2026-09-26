// Drawing a historical BC Hydro signature as SVG.
//
// Framework-free string building over hydroScene(), like every other renderer here, so the gallery
// card, the preview and the download are one drawing. The lettering is outlined by default
// — the same on every machine, with no font to install — and can be kept as live text instead, set
// in the serif the layout was measured with.

import { FLAME, FULL_STAR, STAR } from './hydroMark.js'
import { effectiveMode, HYDRO_GROUPS, HYDRO_PRESETS, HYDRO_TYPES, hydroPalette, hydroScene, productionSpec, sourceKeys, validateHydro } from './hydroLayout.js'
import { escapeXml, num, runMarkup } from './hydroType.js'

const NS = 'http://www.w3.org/2000/svg'

// Every inline SVG on a page shares one id space, and the gallery shows many signatures at once.
let serial = 0

/** The ring's counter, cut out of the flame so the ground shows through it. */
const ringHole = (radius) =>
  ` M ${500 + radius} 500 A ${radius} ${radius} 0 1 0 ${500 - radius} 500 A ${radius} ${radius} 0 1 0 ${500 + radius} 500 Z`

/** The symbol: a ring, or the Gas flame, round the two-star H. */
export const symbolMarkup = (symbol, id) => {
  const { colours } = symbol
  const place = `translate(${num(symbol.x)} ${num(symbol.y)}) scale(${num(symbol.size / 1000)})`
  const gas = symbol.variant === 'gas'
  const outer = gas
    ? `<path id="${id}-flame" fill="${escapeXml(colours.lower)}" fill-rule="evenodd" d="${FLAME + ringHole(500 - symbol.ring)}"/>`
    : `<circle id="${id}-ring" cx="500" cy="500" r="${num(500 - symbol.ring / 2)}" fill="none" stroke="${escapeXml(colours.ink)}" stroke-width="${num(symbol.ring)}"/>`
  // The H always matches the flame; on the ring its halves are green over blue.
  const upper = gas ? colours.lower : colours.upper
  return `<g id="${id}" transform="${place}">${outer}` +
    `<g transform="translate(500 500) scale(${num(symbol.star)}) translate(-500 -500)">` +
    `<path id="${id}-lower" fill="${escapeXml(colours.lower)}" d="${FULL_STAR}"/>` +
    `<path id="${id}-upper" fill="${escapeXml(upper)}" d="${STAR}"/></g></g>`
}

/** Everything drawn, without the document around it. */
export const hydroBodyMarkup = (scene, { prefix = 'bch', guides = false, outline = true } = {}) => {
  const { ink } = hydroPalette(scene.settings)
  let body = scene.symbols.map((symbol, i) => symbolMarkup(symbol, `${prefix}-emblem-${i + 1}`)).join('')
  body += scene.runs.map((run) => runMarkup(run, { fill: ink, outline, id: `${prefix}-${run.id}` })).join('')

  const { border } = scene
  if (border?.visible) {
    body += `<rect id="${prefix}-sign-border" x="${num(border.x)}" y="${num(border.y)}" width="${num(border.right - border.x)}" ` +
      `height="${num(border.bottom - border.y)}" fill="none" stroke="${escapeXml(ink)}" stroke-width="${num(border.stroke)}"/>`
  }
  // Guides are for the preview only: the lines a sign is measured along, labelled.
  if (guides && border) {
    const size = num(scene.metrics.capHeight * 0.07)
    body += `<g id="${prefix}-guides" fill="#ae285c" stroke="#ae285c" font-family="Helvetica, Arial, sans-serif" font-size="${size}">` +
      scene.guides.map((guide) =>
        `<line x1="${num(border.x)}" x2="${num(border.right)}" y1="${num(guide.y)}" y2="${num(guide.y)}" stroke-width="1" stroke-dasharray="5 4"/>` +
        `<text x="${num(border.x + 4)}" y="${num(guide.y - 5)}" stroke="none">${escapeXml(guide.label)}</text>`).join('') +
      '</g>'
  }
  return body
}

const titleOf = (settings) => HYDRO_PRESETS[settings.preset]?.name || HYDRO_TYPES[settings.type]

/**
 * A signature as a complete SVG document.
 *
 * @param {object} settings                 One preset's settings (see hydroDefaults()).
 * @param {object} [options]
 * @param {number} [options.width]          Pixel width written on the root; the view box is fixed.
 * @param {boolean} [options.outline=true]  Letters as paths, or live text.
 * @param {boolean} [options.metadata=true] Carry the settings, the print recipe and the rule checks.
 * @param {boolean} [options.guides=false]  Draw a sign's measuring lines.
 * @param {string} [options.prefix]         Id prefix; unique per render by default.
 * @returns {{svg: string, scene: object}}
 */
export const renderHydroSvg = (settings, {
  width = settings.exportWidth,
  outline = true,
  metadata = true,
  guides = false,
  prefix = `bch-${++serial}`
} = {}) => {
  const scene = hydroScene(settings)
  const view = scene.view
  const height = Math.max(1, Math.round(width * view.height / view.width))
  const background = settings.background === 'transparent' ? null : settings.backgroundColour
  const info = metadata
    ? {
        schema: 'bc-hydro-template/v2',
        settings,
        effectiveMode: effectiveMode(settings),
        production: productionSpec(settings),
        metrics: scene.metrics,
        sourceRules: sourceKeys(settings),
        warnings: validateHydro(settings, scene).filter((note) => note.kind !== 'info').map((note) => note.text)
      }
    : null

  const svg = `<svg xmlns="${NS}" width="${Math.round(width)}" height="${height}" ` +
    `viewBox="${[view.x, view.y, view.width, view.height].map(num).join(' ')}" role="img" aria-labelledby="${prefix}-title">` +
    `<title id="${prefix}-title">${escapeXml(titleOf(settings))} — historical B.C. Hydro reconstruction</title>` +
    (info
      ? `<desc>Unofficial reconstruction from a historical BC Hydro identity manual; not current BC Hydro brand guidance. ` +
        `Lettering is set in TeX Gyre Termes, a substitute for the unrecovered original. Screen colours are approximations; ` +
        `the manual’s print recipe is kept in the metadata.</desc>` +
        `<metadata id="${prefix}-settings">${escapeXml(JSON.stringify(info))}</metadata>`
      : '') +
    (background
      ? `<rect id="${prefix}-background" x="${num(view.x)}" y="${num(view.y)}" width="${num(view.width)}" height="${num(view.height)}" fill="${escapeXml(background)}"/>`
      : '') +
    hydroBodyMarkup(scene, { prefix, guides, outline }) +
    '</svg>'

  return { svg, scene }
}

/**
 * A specimen sheet: every preset in a group — or all of them — on one page, two to a row, each
 * labelled with what it is.
 *
 * @param {Record<string, object>} all  Every preset's settings.
 * @param {string} [group='all']
 */
export const renderHydroSheet = (all, group = 'all', { outline = true } = {}) => {
  const entries = Object.entries(all).filter(([id]) => group === 'all' || HYDRO_PRESETS[id]?.group === group)
  const width = 1600
  const cellWidth = 720
  const cellHeight = 360
  const rows = Math.ceil(entries.length / 2)
  const height = 175 + rows * cellHeight + 70
  const heading = group === 'all' ? `${entries.length} template presets` : HYDRO_GROUPS[group]
  const sans = 'Helvetica, Arial, sans-serif'

  let body = `<rect width="${width}" height="${height}" fill="#f6f7f2"/>` +
    `<g font-family="${sans}" fill="#183c38">` +
    `<text x="60" y="55" font-size="13" letter-spacing="2">HISTORICAL IDENTITY / RECONSTRUCTION</text>` +
    `<text x="60" y="98" font-size="32">B.C. Hydro — ${escapeXml(heading)}</text>` +
    `<text x="60" y="128" font-size="14">Rules transcribed from the manual · approximate screen colours · lettering in TeX Gyre Termes</text></g>`

  entries.forEach(([id, settings], i) => {
    const x = 60 + (i % 2) * 760
    const y = 160 + Math.floor(i / 2) * cellHeight
    const scene = hydroScene({ ...settings, showGuides: false, emblemOnly: false })
    const view = scene.view
    const scale = Math.min((cellWidth - 40) / view.width, 268 / view.height)
    const dx = x + (cellWidth - view.width * scale) / 2
    const dy = y + 62 + (265 - view.height * scale) / 2
    const preset = HYDRO_PRESETS[id]
    body += `<rect x="${x}" y="${y}" width="${cellWidth}" height="${cellHeight - 20}" rx="10" fill="#ffffff" stroke="#d3dcd6"/>` +
      `<g font-family="${sans}" fill="#183c38"><text x="${x + 20}" y="${y + 28}" font-size="15">${escapeXml(preset.name)}</text>` +
      `<text x="${x + 20}" y="${y + 49}" font-size="11" fill="#626f68">${escapeXml(preset.caption)}</text></g>` +
      `<g transform="translate(${num(dx)} ${num(dy)}) scale(${num(scale)}) translate(${num(-view.x)} ${num(-view.y)})">` +
      (settings.background !== 'transparent'
        ? `<rect x="${num(view.x)}" y="${num(view.y)}" width="${num(view.width)}" height="${num(view.height)}" fill="${escapeXml(settings.backgroundColour)}"/>`
        : '') +
      hydroBodyMarkup(scene, { prefix: `sheet-${id}`, outline }) +
      '</g>'
  })

  body += `<text x="60" y="${height - 32}" font-family="${sans}" font-size="12" fill="#626f68">` +
    'Not original artwork masters. Typeface and screen colours are substitutes. No absolute minimum size or exact enlargement factor is supplied.</text>'

  return `<svg xmlns="${NS}" width="${width}" height="${height}" viewBox="0 0 ${width} ${height}" role="img" aria-label="Historical B.C. Hydro template specimen">${body}</svg>`
}
