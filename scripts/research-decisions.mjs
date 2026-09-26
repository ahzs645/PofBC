// Editorial decisions (research/decisions.json), applied to the research as the builds read it.
//
// The research records what the sources say, disagreements included; a decision records which
// reading the atlas uses and why. Applying one replaces the field it names on the record it names,
// resolves the record's status if the decision says so, and leaves the reasoning on the record so
// the panel can show it. The research files are never edited.

import { existsSync, readFileSync } from 'node:fs'
import { resolve } from 'node:path'

/** The decisions beside a research directory (its parent, for research/history). */
export const readDecisions = (dir) => {
  for (const path of [resolve(dir, 'decisions.json'), resolve(dir, '../decisions.json')]) {
    if (existsSync(path)) return JSON.parse(readFileSync(path, 'utf8')).decisions ?? []
  }
  return []
}

const FIELDS = new Set(['established', 'ended'])

/**
 * Applies the decisions about one collection ("sub-agencies") to its records, in place.
 * @returns {string[]} the ids of decisions that matched no record, so a typo is not silent
 */
export const applyDecisions = (collection, records, decisions) => {
  const unmatched = []
  for (const decision of decisions) {
    const [kind, id] = String(decision.subject).split('/')
    if (kind !== collection) continue
    const record = records.find((entry) => entry.id === id)
    if (!record || !FIELDS.has(decision.field)) {
      unmatched.push(decision.id)
      continue
    }
    record[decision.field] = { ...decision.value }
    if (decision.status) record.evidence_status = decision.status
    // A competing claim the decision adopted is now the start itself, not a rival to it.
    record.date_claims = (record.date_claims ?? []).filter((claim) =>
      !(claim.date === decision.value.date && claim.source === decision.value.source))
    ;(record.decisions ??= []).push({ id: decision.id, field: decision.field, reason: decision.reason, setAside: decision.set_aside ?? [], decided: decision.decided })
  }
  return unmatched
}
