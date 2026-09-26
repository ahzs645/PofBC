// The ministry history, made fit to draw a year from.
//
// src/ministries/history.js is the BC Archives diagram's names and years, and for a list of names
// that is enough. A timeline asks more of it — which ministries stood on a given day, and which
// one each became — and two things in it do not survive the question:
//
//   * Eleven episodes have no end year although the ministry was plainly renamed. A timeline that
//     believed them would still show the 1986 Ministry of Post-Secondary Education in 2026.
//   * Renames are keyed by name, and a name can run three times. Forests from 2022 would appear to
//     become Forests and Lands, which it did in 1986. Here each rename is bound to the particular
//     episodes it joins: the one that ended the year the other began.
//
// Neither is corrected in history.js, which is a faithful record of its source. The corrections
// below are this view's reading of it, each with where it came from, and the history after the
// source's last revision (2024-12-16) is added the same way.

import { EPISODES, RENAMES } from '../ministries/history.js'

/**
 * Ends the source leaves open, and the year each ended.
 *
 * From the ministries' own cabinet records (Wikipedia's per-premier ministry tables) and, for the
 * 2025 change, the Province's announcement.
 */
const CLOSED = {
  'Ministry of Energy, Mines and Low Carbon Innovation': 2024,
  'Ministry of Jobs, Economic Development and Competitiveness': 2020,
  'Ministry of Jobs, Economic Recovery and Innovation': 2022,
  'Ministry of Jobs, Economic Development and Innovation': 2025,
  'Ministry of Land, Water and Resource Stewardship': 2022,
  'Ministry of Post-Secondary Education': 1986,
  // Merged with the Attorney General into Justice in 2012, and made again in 2017; the source runs
  // the two periods together as one that never ended.
  'Ministry of Public Safety and Solicitor General': 2012
}

/** Episodes after the source's last revision. */
const LATER = [
  { name: 'Ministry of Public Safety and Solicitor General', from: 2017, to: null, date: '2017-07-18' },
  { name: 'Ministry of Jobs and Economic Growth', from: 2025, to: null, date: '2025-07-17' }
]

/**
 * Lineage the source leaves out: Public Safety's merger into Justice and its return, the
 * November 2024 restructure's splits and merges, which the source records as ministries ending and
 * beginning without joining them, and the 2025 rename.
 */
const LATER_RENAMES = [
  ['Ministry of Public Safety and Solicitor General', 'Ministry of Justice'],
  ['Ministry of Justice', 'Ministry of Public Safety and Solicitor General'],
  ['Ministry of Energy, Mines and Low Carbon Innovation', 'Ministry of Energy and Climate Solutions'],
  ['Ministry of Energy, Mines and Low Carbon Innovation', 'Ministry of Mining and Critical Minerals'],
  ['Ministry of Environment and Climate Change Strategy', 'Ministry of Environment and Parks'],
  ['Ministry of Housing', 'Ministry of Housing and Municipal Affairs'],
  ['Ministry of Municipal Affairs', 'Ministry of Housing and Municipal Affairs'],
  ['Ministry of Transportation and Infrastructure', 'Ministry of Transportation and Transit'],
  ['Ministry of Transportation and Infrastructure', 'Ministry of Infrastructure'],
  ['Ministry of Jobs, Economic Development and Innovation', 'Ministry of Jobs and Economic Growth']
]

/** Names the source spells otherwise than the Province does. */
const SPELLING = {
  "Ministry of Citizen's Services": 'Ministry of Citizens’ Services'
}

/** The ministries in office today, which are the only episodes that may stay open. */
export const CURRENT_MINISTRIES = [
  'Ministry of Agriculture and Food',
  'Ministry of Attorney General',
  'Ministry of Children and Family Development',
  'Ministry of Citizens’ Services',
  'Ministry of Education and Child Care',
  'Ministry of Emergency Management and Climate Readiness',
  'Ministry of Energy and Climate Solutions',
  'Ministry of Environment and Parks',
  'Ministry of Finance',
  'Ministry of Forests',
  'Ministry of Health',
  'Ministry of Housing and Municipal Affairs',
  'Ministry of Indigenous Relations and Reconciliation',
  'Ministry of Infrastructure',
  'Ministry of Jobs and Economic Growth',
  'Ministry of Labour',
  'Ministry of Mining and Critical Minerals',
  'Ministry of Post-Secondary Education and Future Skills',
  'Ministry of Public Safety and Solicitor General',
  'Ministry of Social Development and Poverty Reduction',
  'Ministry of Tourism, Arts, Culture and Sport',
  'Ministry of Transportation and Transit',
  'Ministry of Water, Land and Resource Stewardship'
]

export const fold = (name) => String(name ?? '')
  .replace(/[‘’ʼ]/g, "'")
  .replace(/\s+/g, ' ')
  .trim()
  .toLowerCase()

export const slugify = (name) => fold(name)
  .replace(/'/g, '')
  .replace(/&/g, ' and ')
  .replace(/[^a-z0-9]+/g, '-')
  .replace(/^-|-$/g, '')

const spell = (name) => SPELLING[name] ?? name

/**
 * Every episode, with an id of its own and an end wherever one can be found.
 *
 * An open end that is neither a current ministry nor corrected above is closed at the start of
 * the episode it was renamed into; `inferredEnd` marks those, so the view can say so.
 */
const buildEpisodes = () => {
  const current = new Set(CURRENT_MINISTRIES.map(fold))
  const renames = [...RENAMES, ...LATER_RENAMES].map(([from, to]) => [spell(from), spell(to)])

  const base = [...EPISODES.map((episode) => ({ ...episode, source: true })), ...LATER].map((episode) => {
    const name = spell(episode.name)
    // Only the source's own open ends are closed; an episode added here says its own end.
    const closed = episode.source ? CLOSED[episode.name] ?? CLOSED[name] : undefined
    return {
      name,
      from: episode.from,
      to: episode.to ?? closed ?? null,
      date: episode.date ?? null
    }
  })

  // A later run of a name the source left open is closed where the next run of the same name,
  // or anything it was renamed into, begins.
  for (const episode of base) {
    if (episode.to !== null || current.has(fold(episode.name))) continue
    const successors = renames
      .filter(([from]) => fold(from) === fold(episode.name))
      .flatMap(([, to]) => base.filter((other) => fold(other.name) === fold(to) && other.from >= episode.from))
      .map((other) => other.from)
    if (successors.length) {
      episode.to = Math.min(...successors)
      episode.inferredEnd = true
    }
  }

  // Ids are the name plus the year it began, since a name alone does not pick out a period.
  return base
    .map((episode) => ({ ...episode, id: `${slugify(episode.name)}-${episode.from}` }))
    .sort((a, b) => a.from - b.from || a.name.localeCompare(b.name))
}

export const MINISTRY_EPISODES = buildEpisodes()

const byId = new Map(MINISTRY_EPISODES.map((episode) => [episode.id, episode]))
export const episodeById = (id) => byId.get(id) ?? null

/**
 * Each rename, bound to the pairs of episodes it joins.
 *
 * A pair of names can be joined more than once — Health became Health Services and back again,
 * twice — so every run of the first name is bound to the run of the second that began closest to
 * when it ended, and never more than a year apart, because a rename that joins a 1986 ministry to a
 * 2022 one is two names coinciding, not a lineage.
 */
const buildLinks = () => {
  const links = []
  const renames = [...RENAMES, ...LATER_RENAMES].map(([from, to]) => [spell(from), spell(to)])
  for (const [fromName, toName] of renames) {
    const froms = MINISTRY_EPISODES.filter((episode) => fold(episode.name) === fold(fromName))
    const tos = MINISTRY_EPISODES.filter((episode) => fold(episode.name) === fold(toName))
    for (const a of froms) {
      if (a.to === null) continue
      let best = null
      for (const b of tos) {
        if (b.id === a.id || b.from < a.from) continue
        const gap = Math.abs(b.from - a.to)
        if (gap <= 1 && (!best || gap < best.gap)) best = { from: a.id, to: b.id, gap }
      }
      if (best && !links.some((link) => link.from === best.from && link.to === best.to)) {
        links.push({ from: best.from, to: best.to })
      }
    }
  }
  return links
}

export const LINEAGE = buildLinks()

/** What an episode became, and what it came from. */
export const successorsOf = (id) => LINEAGE.filter((link) => link.from === id).map((link) => byId.get(link.to))
export const predecessorsOf = (id) => LINEAGE.filter((link) => link.to === id).map((link) => byId.get(link.from))

/**
 * Whether an episode stood at the end of `year`.
 *
 * A year is read as its last day, so the year of a reorganisation shows the government it ended
 * with rather than both at once. The exception is an episode that began and ended within a single
 * year, which would otherwise never appear at all.
 */
export const standsIn = (episode, year) => {
  if (episode.from > year) return false
  if (episode.to === null) return true
  if (episode.to === episode.from) {
    // Renamed within the year it began: its successor stands for it at the year's end.
    return year === episode.from && !successorsOf(episode.id).some((next) => next.from === year)
  }
  // Where every successor began the year after, the ministry stood until it was replaced, rather
  // than leaving a year with neither.
  if (isBridged(episode)) return episode.to >= year
  return episode.to > year
}

const isBridged = (episode) => {
  const next = successorsOf(episode.id)
  return next.length > 0 && next.every((successor) => successor.from === episode.to + 1)
}

/**
 * The forerunner of an episode that stood in `year`, found by walking its lineage back — the
 * nearest one, breadth first, since a merger has several.
 */
export const forerunnerIn = (id, year) => {
  const seen = new Set()
  let frontier = [byId.get(id)].filter(Boolean)
  while (frontier.length) {
    const found = frontier.find((episode) => standsIn(episode, year))
    if (found) return found
    frontier.forEach((episode) => seen.add(episode.id))
    frontier = frontier.flatMap((episode) => predecessorsOf(episode.id)).filter((episode) => episode && !seen.has(episode.id))
  }
  return null
}

/** The ministries (or, before 1976, departments) standing at the end of `year`. */
export const episodesIn = (year) => MINISTRY_EPISODES.filter((episode) => standsIn(episode, year))

/**
 * What changed in `year`: episodes that began, and episodes that ended, joined up by lineage
 * where the lineage is known. The shapes follow the change vocabulary of the view this one is
 * modelled on — established, renamed, merged, split, dissolved.
 */
export const changesIn = (year) => {
  const began = MINISTRY_EPISODES.filter((episode) => episode.from === year)
  const ended = MINISTRY_EPISODES.filter((episode) => episode.to === year)
  const accounted = new Set()
  const events = []

  for (const episode of began) {
    const before = predecessorsOf(episode.id).filter((previous) => previous.to === year || previous.to === year - 1 || previous.to === year + 1)
    if (!before.length) {
      events.push({ type: 'established', successors: [episode], predecessors: [] })
      continue
    }
    const splitFrom = before.length === 1 ? successorsOf(before[0].id) : []
    const type = before.length > 1 ? 'merged' : splitFrom.length > 1 ? 'split' : 'renamed'
    // A split is one event however many ministries it made.
    if (type === 'split' && accounted.has(before[0].id)) continue
    const successors = type === 'split' ? splitFrom.filter((next) => next.from === episode.from) : [episode]
    before.forEach((previous) => accounted.add(previous.id))
    events.push({ type, predecessors: before, successors })
  }

  for (const episode of ended) {
    if (accounted.has(episode.id)) continue
    if (successorsOf(episode.id).length) continue
    events.push({ type: 'dissolved', predecessors: [episode], successors: [] })
  }

  return events
}
