// The catalogue of legislation, orders and policy documents (instrumentsData.js), read from either
// side: a body's instruments, and an instrument's bodies.

import { INSTRUMENTS } from './instrumentsData.js'

export { INSTRUMENTS }

/** What each relationship says, in the order a body's card lists them. */
export const RELATIONS = {
  established_by: { label: 'Established by', reverse: 'Established' },
  continued_under: { label: 'Continued under', reverse: 'Continued' },
  reorganized_by: { label: 'Reorganized or renamed by', reverse: 'Reorganized or renamed' },
  administers: { label: 'Administers', reverse: 'Administered by' },
  ended_by: { label: 'Ended by', reverse: 'Ended' },
  current_legal_basis: { label: 'Legal basis today', reverse: 'The legal basis today of',
    note: 'As the current consolidation cites it: what the body stands on now, not when it began.' },
  announced: { label: 'Policy announced', reverse: 'Announced by' }
}

export const TYPES = {
  act: 'Act', regulation: 'Regulation', order_in_council: 'Order in Council',
  ministerial_order: 'Ministerial order', policy: 'Policy document'
}

const byId = new Map(INSTRUMENTS.map((entry) => [entry.id, entry]))
export const instrumentById = (id) => byId.get(id) ?? null

const order = Object.keys(RELATIONS)

/**
 * A body's instruments: each relationship the catalogue states for it, grouped by kind, and the
 * instruments only cited in its history (an Act's assent, a commencement) with no stated relationship.
 */
export const instrumentsOfBody = (id) => {
  if (!id) return { groups: [], cited: [] }
  const rows = INSTRUMENTS.flatMap((instrument) => instrument.relations
    .filter((relation) => relation.body === id)
    .map((relation) => ({ instrument, relation })))
  const related = new Set(rows.map((row) => row.instrument.id))
  const cited = INSTRUMENTS.filter((instrument) => !related.has(instrument.id) &&
    instrument.milestones.some((milestone) => milestone.subject === id || milestone.related.includes(id)))
  const groups = order.map((kind) => ({ kind, ...RELATIONS[kind], rows: rows.filter((row) => row.relation.relation === kind)
    .sort((a, b) => String(a.relation.from ?? '').localeCompare(String(b.relation.from ?? ''))) }))
    .filter((group) => group.rows.length)
  return { groups, cited }
}

/** An instrument's bodies, grouped by what it did for them. */
export const bodiesOfInstrument = (instrument) => order
  .map((kind) => ({ kind, ...RELATIONS[kind], rows: instrument.relations.filter((relation) => relation.relation === kind) }))
  .filter((group) => group.rows.length)
