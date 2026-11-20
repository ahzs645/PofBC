// A ministry's mark as the Province would have set it in a given year.
//
// This is what the generator adds to a diagram of the government: every identity it draws is
// dated, so a ministry picked out on the timeline can be shown in the lockup of its own day — the
// flag for a 1986 ministry, the arms for 2001, the sun and mountains since 2005 — and opened in the
// generator to be made properly.

import { renderCrestSvg } from '../crest/renderCrestSvg.js'
import { renderCurrentSvg } from '../current/currentMarks.js'
import { renderFlagSvg } from '../flag/renderFlagSvg.js'
import { TRANSPARENT } from '../logo/logoColors.js'
import { renderLockupSvg } from '../logo/renderLogoSvg.js'
import { IDENTITY_ERAS } from './timelineData.js'
import { currentMarkFor, generatorPatchFor } from './generatorPatch.js'

/**
 * The identity a lockup made in `year` would most likely have taken, or null before the first one
 * the generator knows. The crest lockups are the earliest it draws and are dated only loosely, so
 * the era reports its own confidence and the view shows it.
 */
export const identityFor = (year) => IDENTITY_ERAS.find((era) => era.from <= year && (era.to === null || year < era.to)) ?? null

// Looking a name up among the published marks, and handing one to the generator, need none of the
// renderers above; generatorPatch.js holds them so the generator can use them without this module.
export { currentMarkFor, generatorPatchFor }

/**
 * The ink each theme sets a one-colour mark in: the interface's own text colour, so a mark reads
 * as part of the page rather than as a picture of a sheet of paper laid on it.
 */
export const MARK_INKS = { light: '#1c1917', dark: '#ede9e2' }

/**
 * The lockup's SVG, drawn for the interface: no background of its own, and in the colourway each
 * identity sanctions for the ground it lands on.
 *
 *   * The current mark takes its Colour version on light and its Reverse version on dark — the
 *     Province's own pair, the second made for BC Blue and black grounds.
 *   * The flag keeps its three inks on light. On dark it goes to one ink, as the flag documents do
 *     on any coloured ground: its white is the page showing through, and a dark page would show
 *     through every stripe.
 *   * The arms and the crest lockups are one-colour marks throughout, set in the page's ink.
 *
 * @param {{era: string, name: string, theme?: 'light'|'dark'}} options
 * @returns {string}
 */
export const renderEraMark = ({ era, name, theme = 'light' }) => {
  const title = `${name}, ${era} identity`
  const dark = theme === 'dark'
  const ink = MARK_INKS[dark ? 'dark' : 'light']
  if (era === 'current') {
    return renderCurrentSvg({ text: currentMarkFor(name)?.en ?? name, variant: dark ? 'reverse' : 'colour', background: TRANSPARENT, title })
  }
  if (era === 'crest') {
    return renderCrestSvg({ ministry: name, markColor: ink, textColor: ink, background: TRANSPARENT, title }).svg
  }
  if (era === 'flag') {
    return renderFlagSvg({ ministry: name, letterColor: ink, textColor: ink, flagPalette: dark ? 'ink' : 'official', background: TRANSPARENT, title }).svg
  }
  return renderLockupSvg({ layout: 'horizontal', ministry: name, markColor: ink, textColor: ink, background: TRANSPARENT, title })
}
