// One ministry, four identities.
//
// The generator used to hold two ministry choices: a list-or-typed name for the three drawn eras,
// and a separate code for the current one. They are the same decision. The current era's mark is
// the same drawing whichever ministry it names — the code only ever looked wording up — so keeping
// two of them meant switching identity quietly changed the name on the lockup, and a name typed by
// hand was lost the moment you went to look at the published mark.
//
// These are the rules that keep the one choice in step across all four.

import { MINISTRIES, findMinistry } from '../current/ministries.js'

/**
 * Names differ between the two lists by punctuation more often than by substance, so they are
 * compared with the apostrophes and the spacing normalised away.
 */
const fold = (name) => String(name ?? '')
  .replace(/[‘’ʼ]/g, "'")
  .replace(/\s+/g, ' ')
  .trim()
  .toLowerCase()

/**
 * The published mark whose English wording is this name, if there is one.
 *
 * The two lists are near-identical — 22 of 23 names match exactly — but they are maintained
 * separately and will drift, so a name that matches nothing is not an error. It simply means the
 * current era has no official wording for it and will typeset the name as given, which is the
 * case this era's typesetting was built for.
 */
export const codeForName = (name) => {
  const wanted = fold(name)
  if (!wanted) return null
  return MINISTRIES.find((ministry) => fold(ministry.en) === wanted)?.code ?? null
}

/** The name the three drawn eras set. */
export const chosenName = (state) =>
  (state.source === 'manual' ? state.manualMinistry : state.ministry).trim()

/**
 * The wording the current era shows, absent a hand edit.
 *
 * A name picked from the list resolves to the Province's own wording where a published mark has
 * one — which is what carries the French, and the two marks whose breaks are written in. Anything
 * else is set as chosen.
 */
export const wordingFor = (state) => {
  if (state.source === 'manual') return state.manualMinistry
  const code = codeForName(state.ministry)
  return (code && findMinistry(code)?.[state.language]) || state.ministry
}
