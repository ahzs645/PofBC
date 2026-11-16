// Handing a ministry from the government diagram to the generator.
//
// Apart from eraMark.js, which draws a ministry's mark in every identity and so brings every
// renderer with it: the generator only needs to know which ministry it has been handed.

import { MINISTRIES as CURRENT_MARKS } from '../current/ministries.js'
import { fold } from './episodes.js'

/** The published wording for a current ministry, if the name is one. */
export const currentMarkFor = (name) => CURRENT_MARKS.find((entry) => fold(entry.en) === fold(name)) ?? null

/**
 * The patch that opens `name` in the generator in `era`.
 *
 * The generator holds one ministry choice for all four identities (src/site/ministryLink.js), so the
 * name goes in through that choice rather than into any one era's field. A ministry with a
 * published mark is chosen from the list, which brings its official wording, French and line
 * breaks with it; anything else is set as a typed name, the way a person would enter it, which
 * every era then shows.
 */
export const generatorPatchFor = ({ era, name }) => {
  const published = currentMarkFor(name)
  return published
    ? { era, source: 'list', ministry: published.en, currentMinistry: published.code, currentNameTouched: false }
    : { era, currentName: name }
}
