// Drawing a one-off mark from its published shapes, in any colours.
//
// The shapes are the artwork's own (src/assets/oneOffMarks.js); only their colours are chosen
// here. Each carries the part it plays — the sun, its rays and core, the mountains, the wordmark,
// the rule and tagline under it, the divider, and the name and its accent beside it — so a
// colourway is a map from part to colour.
//
// The sun can be drawn two ways. As published, it glows: the rays and core fade from the sun's
// colour to the light, which is how the print files shade it. Flat, it is the one-ink mark: the sun
// in its colour, and the rays and core cut out of it in the light's.

import { ONE_OFF_MARKS } from '../assets/oneOffMarks.js'
import { TRANSPARENT, parseHex, resolveColor } from '../logo/logoColors.js'

/** The parts a mark may have, in drawing order. */
export const ONE_OFF_ROLES = ['sun', 'rays', 'core', 'mountains', 'wordmark', 'rule', 'tagline', 'divider', 'name', 'accent', 'leaf']

const escapeXml = (value) => String(value)
  .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;')

const round = (value) => Math.round(value * 1000) / 1000

/** A colour part of the way from `from` to `to`, or null when either is not a plain hex colour. */
const mix = (from, to, amount) => {
  const a = parseHex(from)
  const b = parseHex(to)
  if (!a || !b) return null
  return '#' + a.map((v, i) => Math.round(v + (b[i] - v) * amount).toString(16).padStart(2, '0')).join('')
}

// Every inline SVG on a page shares one id space, and the gallery shows several marks at once.
let serial = 0

/**
 * A one-off mark as SVG.
 *
 * @param {object} options
 * @param {string} options.id                The mark, a key of ONE_OFF_MARKS.
 * @param {object} [options.colours]         Part → colour; anything missing is as published.
 * @param {'glow'|'flat'} [options.sun]      The published shading, or the one-ink sun.
 * @param {number} [options.clearSpaceFactor] Margin as a fraction of the mark's width.
 * @param {string} [options.idPrefix]        Prefix for gradient ids; unique per render by default.
 */
export const renderOneOffSvg = ({ id, colours = {}, sun = 'glow', clearSpaceFactor = 0, idPrefix } = {}) => {
  const mark = ONE_OFF_MARKS[id]
  if (!mark) throw new Error(`no one-off mark called ${id}`)

  const colourOf = (role) => resolveColor(colours[role] ?? mark.printed[role], TRANSPARENT)
  const light = colourOf('light')
  const gold = colourOf('sun')
  const prefix = idPrefix ?? `one-off-${++serial}`

  // A glow needs both ends to be real colours. Given anything else — a transparent light, say —
  // the sun is drawn flat rather than guessed at.
  const glowing = sun === 'glow' && Boolean(mix(light, gold, 0))

  const defs = []
  const fills = {}
  for (const role of ['sun', 'rays', 'core']) {
    // A mark drawn with a flat sun, like StrongerBC, has no shading to glow with.
    const stops = mark.gradients[role]
    if (!glowing || !stops) {
      fills[role] = role === 'sun' ? gold : light
      continue
    }
    const gradientId = `${prefix}-${role}`
    const outer = stops.at(-1)[0] || 1
    defs.push(`<radialGradient id="${gradientId}" gradientUnits="userSpaceOnUse" cx="${mark.sun.cx}" cy="${mark.sun.cy}" r="${round(mark.sun.r * outer)}">` +
      stops.map(([offset, amount]) => `<stop offset="${round(offset / outer)}" stop-color="${mix(light, gold, amount)}"/>`).join('') +
      '</radialGradient>')
    fills[role] = `url(#${gradientId})`
  }

  const padding = clearSpaceFactor * mark.width
  const box = { x: -padding, y: -padding, width: mark.width + padding * 2, height: mark.height + padding * 2 }
  const background = resolveColor(colours.background ?? mark.printed.background, TRANSPARENT)

  const parts = mark.shapes.map(({ role, d }) => {
    const fill = fills[role] ?? colourOf(role)
    // A part with no colour is left out, so whatever is behind shows through.
    if (!fill || fill === TRANSPARENT) return ''
    return `<path data-role="${role}" d="${d}" fill="${escapeXml(fill)}"/>`
  })

  const svg = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="${round(box.x)} ${round(box.y)} ${round(box.width)} ${round(box.height)}">` +
    (defs.length ? `<defs>${defs.join('')}</defs>` : '') +
    (background && background !== TRANSPARENT
      ? `<rect x="${round(box.x)}" y="${round(box.y)}" width="${round(box.width)}" height="${round(box.height)}" fill="${escapeXml(background)}"/>`
      : '') +
    parts.join('') +
    '</svg>'

  return { svg, box }
}

/** The parts a mark actually has, so a colour control is offered only for those. */
export const rolesOf = (id) => {
  const present = new Set(ONE_OFF_MARKS[id].shapes.map(({ role }) => role))
  return ONE_OFF_ROLES.filter((role) => present.has(role))
}

/** Whether a mark was published with a shaded sun, so has a glow to offer at all. */
export const hasGlow = (id) => Object.keys(ONE_OFF_MARKS[id].gradients).length > 0
