// Lookups over the generated BC Laws "Acts – Ministers' Responsibilities" data.
//
// An assignment's effectiveFrom/effectiveTo has a date only when an Order in Council dates it
// (basis "oic-resume" or "oic-checked"); "bounded" gives the two snapshots it fell between, and
// "before-coverage" means it was already listed in the first snapshot (December 2015). A listing's
// period is the span its pages state and is never an effective date: show it as "listed".

import { AMR_ASSIGNMENTS, AMR_CHANGES, AMR_LISTINGS, AMR_SOURCE } from './amrData.js'

export { AMR_ASSIGNMENTS, AMR_CHANGES, AMR_LISTINGS, AMR_SOURCE }

/** The statreg id the generated data keys an Act by, without the "statreg:" prefix. */
const statregOf = (assignment) => assignment.act.statregId

/** Assignments held, for at least one snapshot, by a minister mapped to this ministry episode. */
export const assignmentsOfEpisode = (episodeId) => AMR_ASSIGNMENTS.filter((assignment) =>
  assignment.episodeId === episodeId || (assignment.episodes ?? []).some((run) => run.episodeId === episodeId))

/** Every minister an Act was listed under, oldest run first. */
export const ministersOfAct = (statregId) => AMR_ASSIGNMENTS
  .filter((assignment) => statregOf(assignment) === statregId)
  .sort((a, b) => a.seenIn.first.localeCompare(b.seenIn.first) || a.ministerTitle.localeCompare(b.ministerTitle))

/** Changes to an Act's ministers between snapshots. */
export const changesOfAct = (statregId) => AMR_CHANGES.filter((change) => change.statregId === statregId)

/** Whether a boundary (effectiveFrom/effectiveTo) carries a date a reader may be shown as one. */
export const isDated = (boundary) => Boolean(boundary?.date) && (boundary.basis === 'oic-resume' || boundary.basis === 'oic-checked')

/** An Act's short title, as AMR lists it ("Hospital") or the catalogue names it ("Hospital Act"), for matching. */
export const actKey = (title) => String(title ?? '').normalize('NFKD').replace(/[̀-ͯ]/g, '')
  .replace(/[’']/g, '').replace(/\s+Act$/i, '').toLowerCase().replace(/[^a-z0-9]+/g, ' ').trim()

const startOf = (assignment) => assignment.effectiveFrom?.date ?? assignment.effectiveFrom?.between?.[0] ?? assignment.seenIn.first
/** Whether an assignment is in the latest (current) listing. */
export const isCurrent = (assignment) => assignment.seenIn.last === 'current'

/**
 * The Acts a ministry episode was listed as administering, one entry per Act: its runs (one per
 * minister title or scope) oldest first, whether any run covers only part of the Act, and whether it
 * is in the current listing.
 */
export const actsOfEpisode = (episodeId) => {
  const byAct = new Map()
  for (const assignment of assignmentsOfEpisode(episodeId)) {
    const key = assignment.act.statregId ?? `title:${actKey(assignment.act.title)}`
    const entry = byAct.get(key) ?? { key, title: assignment.act.title, statregId: assignment.act.statregId ?? null, runs: [] }
    entry.runs.push(assignment)
    byAct.set(key, entry)
  }
  return [...byAct.values()].map((entry) => {
    const runs = entry.runs.sort((a, b) => startOf(a).localeCompare(startOf(b)))
    return { ...entry, runs, partial: runs.some((run) => run.scope === 'partial'), current: runs.some(isCurrent) }
  }).sort((a, b) => a.title.localeCompare(b.title))
}

/**
 * The assignments of the Act with this short title, when exactly one BC Laws document carries it.
 * A title two Acts share (two Gaming Control Acts) returns `ambiguous` rather than mixing them.
 */
export const assignmentsOfActTitle = (title) => {
  const key = actKey(title)
  const rows = AMR_ASSIGNMENTS.filter((assignment) => actKey(assignment.act.title) === key)
  const ids = new Set(rows.map((assignment) => assignment.act.statregId ?? null))
  if (ids.size > 1) return { ambiguous: true, statregIds: [...ids], assignments: [] }
  return { ambiguous: false, statregId: [...ids][0] ?? null, assignments: rows.sort((a, b) => startOf(a).localeCompare(startOf(b))) }
}

/** The BC Laws page of an Act, by its document ID. */
export const statregUrl = (statregId) => statregId ? `https://www.bclaws.gov.bc.ca/civix/document/id/complete/statreg/${statregId}` : null
