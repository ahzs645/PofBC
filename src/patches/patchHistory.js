// What the BC Forest Service timeline says about a patch's wording: when the body it names, or the
// thing it shows, came about. A patch can only be as old as its words, so the dates bound it; they
// don't date the patch itself. Matched on the patch's label, so a Forest Oval variant picks up its
// own wording (Ministry of Forests, Airtanker Operations, Wildfire Service).
//
// The Forest Oval cards are also PofBC's own Internal Logos (Internal Logos → Forests), which keep
// their dated research there; a patch links to it rather than repeating it.

import { FOREST_LOGOS } from '../internal/forestLogos.js'

export const FOREST_SERVICE_TIMELINE = {
  title: 'BC Forest Service timeline (BC Forest Service Centenary Society, compiled by John Parminter)',
  url: 'https://bcfs100.for.gov.bc.ca/bscripts/timeline.asp'
}

const FOREST_SERVICE = /Forest\s*\/?\s*Service/i

/** Timeline entries, tried in order; a patch gets every one its label matches. */
const NOTES = [
  {
    id: 'lands-department',
    test: (label) => /Lands Department/i.test(label),
    era: '1912–1945',
    text: 'The Forest Branch was created in the Department of Lands in February 1912, and became the BC Forest Service in 1945, when forests became a department under the Minister of Lands and Forests.'
  },
  {
    id: 'forest-service-parks',
    test: (label) => FOREST_SERVICE.test(label) && /Parks/i.test(label),
    era: '1945–1957',
    text: 'The Forest Branch took on provincial parks in 1939 and the Forest Service formed a Parks and Recreation Division in 1948; parks moved to the Department of Recreation and Conservation in 1957.'
  },
  {
    id: 'recreation-conservation',
    test: (label) => /Recreation and Conservation/i.test(label),
    era: 'From 1957',
    text: 'Parks administration moved from the Forest Service to the Department of Recreation and Conservation in 1957.'
  },
  {
    id: 'department-of-forests',
    test: (label) => /Department of Forests/i.test(label),
    era: '1945–1979',
    text: 'Forests became a department under the Minister of Lands and Forests in 1945, and a Department of Forests of its own in 1976; the Ministry of Forests Act came into force on 1 January 1979.'
  },
  {
    id: 'ministry-of-forests',
    test: (label) => /Ministry of Forests(?!,)/i.test(label),
    era: 'From 1976',
    text: 'A Department of Forests was separated from the Department of Lands in 1976; its Act became the Ministry of Forests Act, in force from 1 January 1979.'
  },
  {
    id: 'forest-service',
    test: (label) => FOREST_SERVICE.test(label) && !/Lands Department|Parks/i.test(label),
    era: 'From 1945',
    text: 'The Forest Branch became the BC Forest Service in 1945. The name outlasted the department: the Forest Service reorganized its districts into regions in 1980, under the Ministry of Forests.'
  },
  {
    id: 'airtanker',
    test: (label) => /Air\s*tanker/i.test(label),
    era: 'From 1958',
    text: 'The first air tankers flew in 1958 (converted Stearmans and Avengers), followed by the A-26 Invader in 1970, the DC-6B in 1973 and the first turbine air tanker, the F-27, in 1986.'
  },
  {
    id: 'wildfire',
    test: (label) => /Wildfire/i.test(label),
    era: 'From 2003',
    text: 'The Wildfire Act was introduced in November 2003. The timeline ends in 2005 and doesn’t record the Wildfire Management or Wildfire Service names themselves.'
  }
]

/** Forest Oval cards (Patcher's consolidated variant groups) and the Internal Logos entry each one is. */
const FOREST_OVAL_LOGOS = {
  'forest-service-oval': 'forest-service',
  'forests-oval': 'forests',
  'long-ministry-oval': 'long-ministry',
  'forest-service-yellow-sky': 'forest-service-yellow-sky',
  'forest-service-green-gold': 'forest-service-green-gold'
}

/**
 * A patch's dated context: the timeline notes its wording matches, and for a Forest Oval, the
 * Internal Logos entry with its evidence line.
 * @returns {{ notes: {id: string, era: string, text: string}[], logo: {id: string, name: string, evidence: string} | null }}
 */
export function historyOf(patch) {
  const notes = NOTES.filter((note) => note.test(patch.label)).map(({ id, era, text }) => ({ id, era, text }))
  const logoId = patch.group ? FOREST_OVAL_LOGOS[patch.group] : undefined
  const logo = logoId ? FOREST_LOGOS.find((entry) => entry.id === logoId) ?? null : null
  return { notes, logo: logo && { id: logo.id, name: logo.name, evidence: logo.evidence } }
}
