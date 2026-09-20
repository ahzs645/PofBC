// What the ministry history is for, here.
//
// Three of this generator's four identities are historical, and its ministry list was not: it held
// the ministries that exist today, so the only names you could set on a 1986 flag lockup were ones
// that did not exist in 1986. The episodes make the older names available, with the years that say
// which lockup they belong on.
//
// A dating aside that fell out of building this, and is worth recording: every ministry named
// across the seventeen flag reference documents existed simultaneously in exactly one year, 1986 —
// Expo year, which is what the Spirit of BC flag was for. The twelve coat-of-arms documents do the
// same thing in 2001. Neither is used to filter anything, because a handful of documents does not
// fix when an identity was in use, but as corroboration that the two sets are what they look like
// it is hard to improve on.

import { EPISODES, RENAMES } from './history.js'

/** Ministries only. The dataset also carries departments, which predate the name. */
const isMinistry = (name) => /^Ministry\b/.test(name)

const fold = (name) => String(name ?? '')
  .replace(/[‘’ʼ]/g, "'")
  .replace(/\s+/g, ' ')
  .trim()
  .toLowerCase()

/**
 * The episodes, newest first, one entry per name-and-period.
 *
 * A name can run more than once — Forests was a ministry from 1976, again from 1988, and again
 * from 2022 — and those are genuinely different periods, so they are kept apart rather than
 * merged into one long run that never happened.
 */
export const MINISTRY_EPISODES = EPISODES
  .filter((episode) => isMinistry(episode.name))
  .slice()
  .sort((a, b) => (b.from ?? 0) - (a.from ?? 0) || a.name.localeCompare(b.name))

/** The years an episode covers, as the list shows them. An open end is left open. */
export const episodeYears = ({ from, to }) => (to ? `${from}–${to}` : `${from}–`)

/**
 * Every episode of a name, newest first.
 *
 * Matching is on the folded name, so a curly apostrophe typed one way finds a record written the
 * other. A name nobody has recorded simply has no episodes, which is not an error — the list has
 * always been a convenience, and a typed name has always been allowed to be anything.
 */
export const episodesOf = (name) => {
  const wanted = fold(name)
  if (!wanted) return []
  return MINISTRY_EPISODES.filter((episode) => fold(episode.name) === wanted)
}

const renamedFrom = (name) => {
  const wanted = fold(name)
  return RENAMES.filter(([from]) => fold(from) === wanted).map(([, to]) => to)
}

/**
 * What a ministry became, following the renames to the end.
 *
 * Returns every end point, because three of the lineages branch: a ministry can be renamed into
 * two, and reporting one of them as *the* successor would be a quiet lie about what happened.
 * Cycles cannot arise from the dataset's shape but are guarded against anyway, since a lineage
 * walk that hangs is a worse failure than one that stops early.
 */
export const becameOf = (name, seen = new Set()) => {
  const key = fold(name)
  if (!key || seen.has(key)) return []
  seen.add(key)

  const next = renamedFrom(name)
  if (!next.length) return []

  const ends = []
  for (const step of next) {
    const onward = becameOf(step, seen)
    for (const end of onward.length ? onward : [step]) {
      if (!ends.some((known) => fold(known) === fold(end))) ends.push(end)
    }
  }
  return ends
}

/**
 * What the field says beneath a chosen name: when it existed, and what it turned into.
 *
 * `null` when there is nothing to say, which is the common case for a name in use today.
 */
export const describeMinistry = (name) => {
  const episodes = episodesOf(name)
  if (!episodes.length) return null

  const latest = episodes[0]
  const became = latest.to ? becameOf(latest.name) : []

  return {
    years: episodeYears(latest),
    ended: latest.to,
    // Earlier runs of the same name, which is the part people do not expect.
    earlier: episodes.slice(1).map(episodeYears),
    became
  }
}

/**
 * The historical names, grouped by the decade they began, for a list spanning a century and a half.
 *
 * One entry per name, not per episode: a name that ran three times would otherwise appear three
 * times over, and since the list is keyed by the name itself the three would be indistinguishable
 * to everything downstream. The earlier runs are not lost — `describeMinistry` reports them once a
 * name is chosen, which is where they are interesting rather than merely repetitive.
 *
 * @param {string[]} [exclude]  Names the caller already offers, so nothing is listed twice.
 */
export const historicalGroups = (exclude = []) => {
  const taken = new Set(exclude.map(fold))
  const groups = new Map()

  for (const episode of MINISTRY_EPISODES) {
    const key = fold(episode.name)
    if (taken.has(key)) continue
    taken.add(key)

    const decade = Math.floor(episode.from / 10) * 10
    if (!groups.has(decade)) groups.set(decade, [])
    groups.get(decade).push(episode)
  }

  return [...groups.entries()]
    .sort(([a], [b]) => b - a)
    .map(([decade, episodes]) => ({
      label: `${decade}s`,
      options: episodes.map((episode) => ({
        value: episode.name,
        label: `${episode.name} (${episodeYears(episode)})`
      }))
    }))
}
