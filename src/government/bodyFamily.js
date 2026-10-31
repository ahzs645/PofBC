// A body's whole family: what it was formed from, generation by generation, and what it went into,
// up to today.
//
// The records join bodies three ways, and each is kept for what it is:
//
//   * became — a body became another: renamed, succeeded, or amalgamated with others (the 44 boards
//     and councils of B.C. Reg. 293/2001 each became one of the five authorities; the councils of
//     1994–95 each became a 1997 board);
//   * services — a body was not amalgamated, but its services passed to one or more others (the
//     community health services societies, 2001–02);
//   * area — part of a body's territory moved to another after the fact, by a dated event
//     (Bella Coola and the Central Coast moved to Vancouver Coastal in March 2002).
//
// So one body can lead to two. The Cariboo society's services went to Interior Health and to
// Northern Health; Bella Coola's council was amalgamated into Interior Health, and its area then
// moved to Vancouver Coastal. Where a body in one family also went elsewhere, it says where
// (`elsewhere`), so the overlap between two authorities' families is shown on both sides rather
// than either claiming the whole.

import { CURRENT_BODIES } from './currentData.js'
import { EVENTS } from './events.js'
import { HISTORICAL_BODIES } from './historyData.js'

const DEPTH = 4
const historical = new Map(HISTORICAL_BODIES.map((body) => [body.id, body]))
const current = new Map(CURRENT_BODIES.map((body) => [body.id, body]))
const recordOf = (id) => historical.get(id) ?? current.get(id) ?? null
const areaMoves = EVENTS.filter((event) => event.type === 'territory_transferred' && event.date?.start)

/** What the panel needs to show and reach a body. */
const brief = (id) => {
  const record = recordOf(id)
  return {
    id,
    name: record?.name ?? id,
    kind: record?.kind ?? 'agency',
    established: record?.established ?? null,
    ended: record?.ended ?? null,
    firstSeen: Array.isArray(record?.firstSeen) ? record.firstSeen[0] ?? null : record?.firstSeen ?? null
  }
}

/** The bodies a body went into, each with how: { id, how, date? }. */
const nextOf = (id) => {
  const record = historical.get(id)
  const next = []
  if (record?.became) next.push({ id: record.became, how: 'became', date: record.ended ?? null })
  for (const to of record?.servicesPassedTo ?? []) next.push({ id: to, how: 'services', date: record.ended ?? null })
  for (const event of areaMoves) {
    if (event.subject !== id && (event.related ?? []).includes(id)) next.push({ id: event.subject, how: 'area', date: event.date.start, title: event.title })
  }
  return next
}

/** The bodies a body was formed from, each with how. */
const previousOf = (id) => {
  const previous = new Map()
  for (const body of HISTORICAL_BODIES) {
    if (body.became === id) previous.set(body.id, { id: body.id, how: 'became', date: body.ended ?? null })
    else if ((body.servicesPassedTo ?? []).includes(id)) previous.set(body.id, { id: body.id, how: 'services', date: body.ended ?? null })
  }
  // A predecessor the record names without saying how.
  for (const from of historical.get(id)?.predecessors ?? []) {
    if (!previous.has(from)) previous.set(from, { id: from, how: 'predecessor', date: recordOf(from)?.ended ?? null })
  }
  // Area moved to it: from the bodies that held it, and the former boards whose area it was.
  for (const event of areaMoves) {
    if (event.subject !== id) continue
    for (const from of event.related ?? []) {
      if (from !== id && !previous.has(from)) previous.set(from, { id: from, how: 'area', date: event.date.start, title: event.title })
    }
  }
  return [...previous.values()]
}

const ORDER = { became: 0, predecessor: 1, services: 2, area: 3 }

const cache = new Map()

/**
 * { formedFrom, wentTo }: each a list of rows in tree order (a body, then the bodies it came from or
 * went into, deeper), each row { ...brief, how, date, depth, parent, elsewhere, count }. `elsewhere`
 * names the other bodies a row's body also went into; `count` how many rows lie beneath it. The walk
 * goes four generations deep, which reaches the oldest records.
 */
export const bodyFamily = (id) => {
  if (cache.has(id)) return cache.get(id)
  const walk = (start, step, other) => {
    const rows = []
    const seen = new Set([start])
    // A move of area is the body's own story, not its family's: it is followed from the body itself
    // and no further, so an authority that gave up a valley does not bring its constituents with it.
    const visit = (at, depth) => {
      if (depth > DEPTH) return 0
      const links = step(at).filter((link) => !seen.has(link.id) && (depth === 1 || link.how !== 'area'))
        .sort((a, b) => ORDER[a.how] - ORDER[b.how] || brief(a.id).name.localeCompare(brief(b.id).name))
      let below = 0
      for (const link of links) {
        if (seen.has(link.id)) continue
        seen.add(link.id)
        // Where the body on this row also went (formed-from rows), or also came from (went-to rows).
        const elsewhere = other(link.id).filter((each) => each.id !== at).map((each) => ({ ...brief(each.id), how: each.how, date: each.date ?? null }))
        const row = { ...brief(link.id), how: link.how, date: link.date ?? null, title: link.title ?? null, depth, parent: at, elsewhere, count: 0 }
        rows.push(row)
        row.count = link.how === 'area' ? 0 : visit(link.id, depth + 1)
        below += 1 + row.count
      }
      return below
    }
    visit(start, 1)
    return rows
  }
  const family = {
    formedFrom: walk(id, previousOf, nextOf),
    // Going forward, `elsewhere` would name every other constituent of a merger: of no help there.
    wentTo: walk(id, nextOf, () => [])
  }
  cache.set(id, family)
  return family
}

/**
 * The heading a group of rows goes under, by how they join the body: in the direction of the walk,
 * and for `became` whether several merged (a body several became was formed by amalgamation).
 */
export const groupTitle = (direction, how, several) => (direction === 'formedFrom'
  ? { became: several ? 'Amalgamated to form it' : 'Came from', predecessor: 'Came from', services: 'Its services came from', area: 'Part of its area came from' }
  : { became: 'Became', predecessor: 'Succeeded by', services: 'Its services passed to', area: 'Part of its area moved to' })[how]

/** How a row's body also went elsewhere, as a line: "also to Interior Health Authority (services)". */
export const elsewhereLine = (row) => (row.elsewhere.length
  ? `Also ${row.elsewhere.map((each) => `${{ became: 'became', predecessor: 'succeeded by', services: 'services to', area: 'area to' }[each.how]} ${each.name}${each.date ? `, ${String(each.date).slice(0, 4)}` : ''}`).join('; ')}`
  : null)
