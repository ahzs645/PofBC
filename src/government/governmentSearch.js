// The government view's search: everything the timeline holds, not just the year on screen.
//
// A ministry that ran from 1986 to 1988 is found, and choosing it moves the timeline there; so is a
// former body, a local one, every minister by name ("Vander Zalm"), and the related public bodies.
//
// Each organization is listed once. A body that still runs is in today's government and also in the
// histories, which record when it began; the two are the same body under the same id, so the history
// lends today's entry its years and is not listed again.

import { MINISTRY_EPISODES } from './episodes.js'
import { governmentIn, lifespanOf, lifeYears, PRESENT_YEAR } from './snapshot.js'
import { RELATED_BODIES, RELATED_BODY_KINDS } from './relatedBodies.js'
import { HISTORICAL_BODIES, MINISTERS, LOCAL_BODIES } from './historyData.js'

const LOCAL_KINDS = new Set(['regional-hospital-district', 'hospital-improvement-district'])

/** Builds the index. Exported for the tests; the view uses `search`. */
export const buildSearchIndex = () => {
  const nodes = governmentIn(PRESENT_YEAR).nodes
  const today = nodes
    .filter((node) => node.kind !== 'ministry')
    .map((node) => ({ id: node.id, name: node.name, alias: node.shortName, year: PRESENT_YEAR, detail: node.head?.person }))
  const episodes = MINISTRY_EPISODES.map((episode) => ({
    id: episode.id,
    name: episode.name,
    year: episode.to === null ? PRESENT_YEAR : episode.to === episode.from ? episode.from : episode.to - 1,
    detail: episode.to ? `${episode.from}–${episode.to}` : `${episode.from}–`
  }))
  // Former bodies, and local ones, found whatever is known of their lives: an untraced end, a start
  // known only by a sighting.
  const bodies = [...HISTORICAL_BODIES.filter((body) => !body.current && body.name), ...LOCAL_BODIES]
    .filter((body) => lifespanOf(body).from)
    .map((body) => {
      const life = lifespanOf(body)
      return {
        id: body.id,
        name: body.name,
        alias: body.shortName,
        year: Number(String(life.from).slice(0, 4)),
        detail: `${lifeYears(life)}${LOCAL_KINDS.has(body.kind) ? ' · local' : ''}`,
        body,
        ...(LOCAL_BODIES.includes(body) ? { local: true } : {})
      }
    })
  const ministers = Object.entries(MINISTERS).flatMap(([episodeId, rows]) => rows.map(([person, from, to, title]) => {
    const episode = MINISTRY_EPISODES.find((entry) => entry.id === episodeId)
    const start = Math.max(Number(String(from).slice(0, 4)), episode?.from ?? 0)
    return { id: episodeId, name: person, alias: title, year: episode?.to && start >= episode.to ? Math.max(episode.from, episode.to - 1) : start, detail: `${title}, ${String(from).slice(0, 4)}–${to ? String(to).slice(0, 4) : ''}`, minister: true }
  }))
  for (const node of nodes.filter((entry) => entry.kind === 'ministry')) {
    for (const official of [node.deputy, ...node.ministersOfState, ...node.parliamentarySecretaries].filter(Boolean)) {
      ministers.push({ id: node.id, name: official.person, year: PRESENT_YEAR, detail: `${official.title} · ${node.name}`, minister: true })
    }
  }
  const related = RELATED_BODIES.map((body) => ({
    id: body.id, name: body.name, alias: [body.shortName, ...body.aliases].join(' '),
    year: PRESENT_YEAR, detail: RELATED_BODY_KINDS[body.kind], related: true
  }))

  // One entry per organization (by id, the first source winning: today, then the histories, then the
  // related bodies), and one per minister's term, since a term that spans a renaming — the 1976
  // departments becoming ministries — is recorded under both names.
  const byId = new Map()
  const seenTerms = new Set()
  const entries = []
  for (const entry of [...today, ...episodes, ...bodies, ...related]) {
    const first = byId.get(entry.id)
    if (first) {
      // The history knows when a body that still runs began; today's entry may have nothing to say.
      if (!first.detail && entry.detail) first.detail = entry.detail
      first.alias = [first.alias, entry.alias].filter(Boolean).join(' ') || undefined
      continue
    }
    const kept = { ...entry }
    byId.set(entry.id, kept)
    entries.push(kept)
  }
  for (const entry of ministers) {
    const term = `${entry.name}|${entry.detail}`
    if (seenTerms.has(term)) continue
    seenTerms.add(term)
    entries.push(entry)
  }
  // Ministers share their ministry's id, so a result is keyed by its place in the index.
  return entries.map((entry, index) => ({ ...entry, key: index }))
}

let index = null
const searchIndex = () => (index ??= buildSearchIndex())

export const normal = (text) => String(text ?? '').toLowerCase().normalize('NFD').replace(/\p{M}/gu, '').replace(/[^a-z0-9 ]+/g, ' ')

/** Up to ten matches for every word of `query`: bodies before people, the most recent first. */
export const search = (query) => {
  const words = normal(query).split(/\s+/).filter(Boolean)
  if (!words.length) return []
  return searchIndex()
    .filter((entry) => {
      // A minister is found by name, not by portfolio, or "forests" would list every minister of it.
      const haystack = normal(entry.minister ? entry.name : `${entry.name} ${entry.alias ?? ''} ${entry.detail ?? ''}`)
      return words.every((word) => haystack.includes(word))
    })
    .sort((a, b) => Number(Boolean(a.minister)) - Number(Boolean(b.minister)) || b.year - a.year)
    .slice(0, 10)
}
