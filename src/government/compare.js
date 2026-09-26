// What changed between two years: the comparison view's account.
//
// Scrubbing a slider and remembering what moved is a poor way to answer "what changed between
// 1986 and 2001?". This answers it directly: which ministries carried on, which became others
// (through renames, mergers and splits, followed along their lineage), which began or ended with no
// forerunner or successor on the other side; which bodies appeared or closed; who changed in the
// offices that persisted; and every dated event in between. Unchanged things are counted, not
// listed, so the changes stand out.

import { MINISTRY_EPISODES, predecessorsOf, standsIn, successorsOf } from './episodes.js'
import { EVENTS, yearOfEvent } from './events.js'
import { governmentIn } from './snapshot.js'

/** The episodes a lineage reaches from `episode` that stand in `year`, walking `next` (forwards or back). */
const reach = (episode, year, next) => {
  const found = []
  const seen = new Set([episode.id])
  let frontier = next(episode.id)
  for (let depth = 0; frontier.length && depth < 12; depth += 1) {
    const following = []
    for (const other of frontier) {
      if (!other || seen.has(other.id)) continue
      seen.add(other.id)
      if (standsIn(other, year)) found.push(other)
      else following.push(...next(other.id))
    }
    frontier = following
  }
  return found
}

const nameOf = (node) => node?.shortName ?? node?.name ?? null

/** The words that say what a ministry is for, without the furniture. */
const STOP = new Set(['ministry', 'department', 'of', 'the', 'and', 'for', 'minister', 'provincial'])
const words = (name) => new Set(String(name).toLowerCase().replace(/[^a-z ]+/g, ' ').split(/\s+/).filter((word) => word && !STOP.has(word)))

/** How alike two names are, as the share of their words they have in common. */
const likeness = (x, y) => {
  const a = words(x)
  const b = words(y)
  const shared = [...a].filter((word) => b.has(word)).length
  return shared / Math.max(1, new Set([...a, ...b]).size)
}

/**
 * @param {number} from  the earlier year
 * @param {number} to    the later year
 */
export const compareYears = (from, to) => {
  const [a, b] = from <= to ? [from, to] : [to, from]
  const before = governmentIn(a)
  const after = governmentIn(b)
  const inA = new Map(before.nodes.map((node) => [node.id, node]))
  const inB = new Map(after.nodes.map((node) => [node.id, node]))

  // Ministries: the same episode on both sides, or a lineage joining them.
  const ministriesA = before.nodes.filter((node) => node.kind === 'ministry')
  const ministriesB = after.nodes.filter((node) => node.kind === 'ministry')
  const continuing = ministriesA.filter((node) => inB.has(node.id))
  const transformed = []
  const ended = []
  for (const node of ministriesA) {
    if (inB.has(node.id)) continue
    const into = reach(node.episode, b, successorsOf)
    if (into.length) transformed.push({ from: node, into })
    else ended.push(node)
  }
  // Where the lineage records nothing, a ministry of the same or a closely similar name on the
  // other side is paired with it — and marked as such, since a shared name is not a recorded lineage.
  const reachedFromA = new Set(transformed.flatMap((entry) => entry.into.map((episode) => episode.id)))
  const unclaimed = () => ministriesB.filter((node) => !inA.has(node.id) && !reachedFromA.has(node.id) &&
    !reach(node.episode, a, predecessorsOf).length)
  for (const node of [...ended]) {
    const best = unclaimed()
      .map((candidate) => ({ candidate, score: likeness(node.name, candidate.name) }))
      .filter(({ score }) => score >= 0.5)
      .sort((x, y) => y.score - x.score)[0]
    if (!best) continue
    ended.splice(ended.indexOf(node), 1)
    transformed.push({ from: node, into: [best.candidate.episode], byName: true })
    reachedFromA.add(best.candidate.id)
  }
  const created = unclaimed()

  // Other bodies — not ministries, not sub-agencies, not the fixed offices.
  const FIXED = new Set(['people', 'assembly', 'crown', 'premier', 'ministry', 'sub'])
  const bodiesA = before.nodes.filter((node) => !FIXED.has(node.kind))
  const bodiesB = after.nodes.filter((node) => !FIXED.has(node.kind))
  const appeared = bodiesB.filter((node) => !inA.has(node.id))
  const closed = bodiesA.filter((node) => !inB.has(node.id))
  const ministryName = (government, id) => nameOf(government.nodes.find((node) => node.id === id))
  const moved = bodiesB
    .filter((node) => inA.has(node.id) && node.group && inA.get(node.id).group && ministryName(before, inA.get(node.id).group) !== ministryName(after, node.group))
    .map((node) => ({ node, from: ministryName(before, inA.get(node.id).group), to: ministryName(after, node.group) }))

  // People in the offices that persisted.
  const person = (node) => node?.head?.person ?? null
  const offices = [
    { label: 'Premier', a: before.premier?.name ?? null, b: after.premier?.name ?? null },
    { label: 'Lieutenant Governor', a: before.lieutenantGovernor?.name ?? null, b: after.lieutenantGovernor?.name ?? null },
    { label: 'Speaker', a: person(inA.get('legislative-assembly')), b: person(inB.get('legislative-assembly')) }
  ].filter((office) => office.a !== office.b)
  const ministers = continuing
    .map((node) => ({ node, a: person(node), b: person(inB.get(node.id)) }))
    .filter((entry) => entry.a && entry.b && entry.a !== entry.b)

  const events = EVENTS.filter((event) => {
    const year = yearOfEvent(event)
    return year > a && year <= b && event.status === 'source_reported_past'
  })

  return {
    from: a,
    to: b,
    ministries: { continuing: continuing.length, transformed, created, ended, before: ministriesA.length, after: ministriesB.length },
    bodies: { appeared, closed, moved, before: bodiesA.length, after: bodiesB.length },
    subAgencies: {
      before: before.nodes.filter((node) => node.kind === 'sub').length,
      after: after.nodes.filter((node) => node.kind === 'sub').length
    },
    offices,
    ministers,
    seats: { before: before.election?.totalSeats ?? null, after: after.election?.totalSeats ?? null },
    events
  }
}

export { MINISTRY_EPISODES }
