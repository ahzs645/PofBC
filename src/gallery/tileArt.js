// A gallery entry's artwork as SVG markup (or an image for a collected file), as its tile draws it:
// on the page's ground in the page's theme, or on a ground of its own. Shared by the gallery and the
// government panel's logo card, which loads it only when a body with logos is opened.

import { renderFlagSvg } from '../flag/renderFlagSvg.js'
import { renderCurrentHydroSvg, renderHydroMarkSvg } from '../hydro/hydroMarks.js'
import { HYDRO_PRESETS, hydroDefaults } from '../hydro/hydroLayout.js'
import { renderHydroSvg } from '../hydro/renderHydroSvg.js'
import { renderOneOffSvg } from './renderOneOff.js'
import { pageColoursFor } from './pageColours.js'
import { ONE_OFF_MARKS } from '../assets/oneOffMarks.js'
import { TRANSPARENT } from '../logo/logoColors.js'
import { renderCurrentSvg } from '../current/currentMarks.js'
import { darkPageInks, renderSuppliedSvg } from './renderSupplied.js'
import { assetUrl } from './collectedCollections.js'

/**
 * What a card shows: the entry drawn for the page it sits on — no ground of its own, in the version
 * its identity sanctions for a light or a dark page (see pageColours.js). BC Hydro's 1961
 * signatures take their white form on dark, as the manual's reverse forms do. The exceptions keep
 * their ground because the ground is the point: the 1961 manual's backgrounds and vehicles, and
 * BC Hydro's current colourways, each of which is defined by what it sits on.
 */
export const tileArt = (entry, theme = 'light', { cover = false } = {}) => {
  if (entry.kind === 'collected') {
    const escape = (value) => String(value).replace(/&/g, '&amp;').replace(/"/g, '&quot;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
    return `<img class="gallery__collected-image" src="${escape(assetUrl(entry.asset.preview || entry.asset.file))}" alt="${escape(entry.label)}" loading="lazy" data-dark="${entry.asset.darkBackground ? 'true' : 'false'}" />`
  }
  if (entry.kind === 'artwork') {
    const printed = ONE_OFF_MARKS[entry.mark].printed
    return renderOneOffSvg({ id: entry.mark, colours: pageColoursFor(printed, theme), sun: 'glow', clearSpaceFactor: 0.02 }).svg
  }
  // The Crown corporations' marks are drawn as supplied: on dark, one supplied reversed takes that
  // version, and any other its page reversal (darkPageInks), with no ground of its own.
  if (entry.kind === 'supplied') {
    const dark = theme === 'dark'
    const id = dark && entry.reverse ? entry.reverse : entry.mark
    const inks = dark && !entry.reverse ? darkPageInks(id, entry.onDark) : null
    return renderSuppliedSvg({ id, inks, clearSpace: 0.02 }).svg
  }
  // Remade in the current identity: drawn by the generator's current era, reversed on dark.
  if (entry.kind === 'current') {
    return renderCurrentSvg({ text: entry.text, variant: theme === 'dark' ? 'reverse' : 'colour', clearSpaceFactor: 0.02 })
  }
  if (entry.kind === 'flag') {
    const dark = theme === 'dark'
    return renderFlagSvg({
      ...entry.draw,
      letterColor: dark ? '#ffffff' : '#10069f',
      textColor: dark ? '#ffffff' : '#10069f',
      flagPalette: dark ? 'ink' : 'official',
      background: TRANSPARENT,
      clearSpaceFactor: 0.02
    }).svg
  }
  if (entry.kind === 'hydro') {
    const settings = hydroDefaults(entry.preset)
    const signature = HYDRO_PRESETS[entry.preset]?.group === 'signature'
    return renderHydroSvg(signature && theme === 'dark' ? { ...settings, mode: 'white' } : settings, { metadata: false, width: 480 }).svg
  }
  if (entry.mark === '1990') return renderHydroMarkSvg({ id: 'bc-hydro-1990', clearSpace: 0.08, background: TRANSPARENT, width: 480 }).svg
  // A collection's cover stands for the whole identity, so it takes the page's version of it.
  if (cover) return renderCurrentHydroSvg({ variant: theme === 'dark' ? 'reverse' : 'colour', background: TRANSPARENT, clearSpace: 0.08, width: 480 }).svg
  return renderCurrentHydroSvg({ variant: entry.variant, clearSpace: 1 / 3, width: 480 }).svg
}

/** Whether a card draws on the page's ground, or keeps a ground of its own. */
export const onPage = (entry) => entry.kind === 'artwork' || entry.kind === 'current' || entry.kind === 'flag' || entry.kind === 'supplied' || entry.mark === '1990' ||
  (entry.kind === 'hydro' && HYDRO_PRESETS[entry.preset]?.group === 'signature')
