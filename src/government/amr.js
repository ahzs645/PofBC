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
