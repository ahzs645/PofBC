import { readFileSync } from 'node:fs'
import { resolve, relative, sep } from 'node:path'
import { gunzipSync } from 'node:zlib'
import { createHash } from 'node:crypto'
import { personKey } from '../../src/salaries/people.js'
import { nameRowsFingerprint } from './reviewed-name-connections.mjs'

const area = 'research/salaries/source-follow-through-2026-11-02'
export const BASELINE_LIKELY_INPUTS = Object.freeze({
  graphPath: `${area}/baseline-live-links.json.gzip`,
  graphSha256: 'c6b77c67224e1bbb554abb76b54b52e815e0861e888cca0081e30b9082a6f47c',
  repeatPath: 'research/salaries/name-links/repeat-reviewed.json',
  repeatSha256: '4acb7b26f25a626dc91aa4df48706b62d0993c31bd1139e48066dded791278b1'
})
export const BASELINE_LIKELY_PAIRS = Object.freeze([
  ['bell|christopher', 'bell|christopher s'],
  ['dangerfield|bruce', 'dangerfield|bruce t'],
  ['dobry|jeffrey', 'dobry|jeffrey henry'],
  ['gouthro|daryl b', 'gouthro|daryl bernard'],
  ['hunsbedt|danel', 'hunsbedt|dan el'],
  ['jimenez|maria c', 'jimenez|maria cristina'],
  ['kiarash|malyam', 'kiarash|maly am'],
  ['kurceba|isabel j', 'kurceba|isabel j j'],
  ['kwan|robert yc', 'kwan|robert y c'],
  ['margach|maryjane', 'margach|mary jane'],
  ['nussbaumer|gary', 'nussbaumer|gary r']
])
const employer = 'provincial-health-services-authority'
const sha = (b) => createHash('sha256').update(b).digest('hex')
const jsonSha = (x) => sha(JSON.stringify(x))
const same = (a, b) => JSON.stringify(a) === JSON.stringify(b)
const sourceIds = (rs) => [...new Set(rs.map((r) => r[6]))].sort()
const sourcePins = (rs, index) => sourceIds(rs).map((id) => ({ sourceId: id, sha256: jsonSha(index.sources[id]) }))
const setKey = (e) => JSON.stringify([e.employer, e.proof?.aliasKey, e.proof?.targetKey])
const wantedSet = BASELINE_LIKELY_PAIRS.map(([a, b]) => JSON.stringify([employer, a, b])).sort()
const histories = (rows, index, slug, surname, nameKey = null) => rows.filter((r) => index.employers[r[4]]?.[3] === slug
  && (nameKey == null ? personKey(r[0]).split('|')[0] === surname : personKey(r[0]) === nameKey))
const historyPin = (rs, index) => ({ rowCount: rs.length, rowsSha256: nameRowsFingerprint(rs, index), sourceIds: sourceIds(rs) })
const union = () => {
  const parents = new Map()
  const find = (k) => { if (!parents.has(k)) parents.set(k, k); if (parents.get(k) !== k) parents.set(k, find(parents.get(k))); return parents.get(k) }
  return { find, join: (a, b) => parents.set(find(a), find(b)) }
}

/** Preserve only11 already-published assumptions. Raw public name keys, complete
 * endpoint AND surname-family histories, baseline graph/index and repeat ledger
 * are immutable gates. No new identity or verified decision is produced.
 */
export const validateBaselineLikelyConnections = (payload, rows, index, baseline, root, { readInput = (path) => readFileSync(resolve(root, path)) } = {}) => {
  if (payload?.schemaVersion !== 1 || payload.scope !== 'preserve-existing-likely-only' || payload.authorization !== 'root-approved-existing-likely-preservation'
    || !Array.isArray(payload.decisions) || payload.decisions.length !== 11 || !Array.isArray(baseline?.rows) || !baseline.index) throw new Error('Invalid11-pair baseline likely continuity receipt')
  if (!same(payload.decisions.map(setKey).sort(), wantedSet)) throw new Error('Only the approved11 old likely pairs may be preserved')
  const pins = new Map()
  for (const pin of payload.inputs ?? []) {
    const p = resolve(root, pin.path)
    if (relative(root, p).startsWith(`..${sep}`) || pins.has(pin.path) || !/^[a-f0-9]{64}$/.test(pin.sha256)) throw new Error('Invalid likely continuity input pin')
    const b = readInput(pin.path)
    if (sha(b) !== pin.sha256) throw new Error(`Likely continuity input changed: ${pin.path}`)
    pins.set(pin.path, { pin, bytes: b })
  }
  const graphPin = pins.get(BASELINE_LIKELY_INPUTS.graphPath), repeatPin = pins.get(BASELINE_LIKELY_INPUTS.repeatPath)
  if (graphPin?.pin.sha256 !== BASELINE_LIKELY_INPUTS.graphSha256 || repeatPin?.pin.sha256 !== BASELINE_LIKELY_INPUTS.repeatSha256) throw new Error('Approved baseline graph/index and repeat ledger must both be pinned')
  const oldIndexPin = pins.get(`${area}/baseline-people-index.json.gzip`)
  if (!oldIndexPin || !same(JSON.parse(gunzipSync(oldIndexPin.bytes)), baseline.index)) throw new Error('Original baseline index context changed')
  const graph = JSON.parse(gunzipSync(graphPin.bytes)), all = union(), verified = union()
  for (const [slug, key, name, aliases] of graph.groups) for (const alias of aliases) {
    const a = `${slug}|${key}`, b = `${slug}|${alias[0]}`
    if (['verified', 'likely'].includes(alias[2])) all.join(a, b)
    if (alias[2] === 'verified') verified.join(a, b)
  }
  for (const e of payload.decisions) {
    const p = e.proof
    if (e.decision !== 'likely' || e.canonicalName || e.names?.length !== 2 || !e.note || e.evidence?.length
      || p.oldStatus !== 'likely' || p.confidenceUpgradeAllowed !== false || p.identityEstablished !== false
      || !same(e.names.map(personKey), [p.aliasKey, p.targetKey]) || e.preferredName !== e.names[1]
      || p.surname !== p.aliasKey.split('|')[0] || p.surname !== p.targetKey.split('|')[0]) throw new Error('Continuity preserves likely only; no new identity or confidence upgrade')
    const edges = graph.groups.flatMap(([slug, key, name, aliases]) => slug === e.employer && key === p.targetKey
      ? aliases.filter((a) => a[0] === p.aliasKey).map((a) => ({ targetName: name, aliasName: a[1], status: a[2], reason: a[3] })) : [])
    if (edges.length !== 1 || edges[0].status !== 'likely' || edges[0].reason !== p.oldReason
      || edges[0].targetName !== e.names[1] || edges[0].aliasName !== e.names[0]
      || all.find(`${e.employer}|${p.aliasKey}`) !== all.find(`${e.employer}|${p.targetKey}`)
      || verified.find(`${e.employer}|${p.aliasKey}`) === verified.find(`${e.employer}|${p.targetKey}`)) throw new Error('An actual prior likely path is required; prior verified paths cannot be downgraded')
    for (const [key, name, pin] of [[p.aliasKey, e.names[0], p.alias], [p.targetKey, e.names[1], p.target]]) {
      const before = histories(baseline.rows, baseline.index, e.employer, p.surname, key), current = histories(rows, index, e.employer, p.surname, key)
      if (!before.length || !current.some((r) => r[0] === name) || !before.some((r) => r[0] === name)
        || !same(historyPin(before, baseline.index), pin) || !same(historyPin(current, index), pin)) throw new Error('Complete old/current alias or target history changed')
    }
    const beforeFamily = histories(baseline.rows, baseline.index, e.employer, p.surname), currentFamily = histories(rows, index, e.employer, p.surname)
    if (!same(historyPin(beforeFamily, baseline.index), p.family) || !same(historyPin(currentFamily, index), p.family)) throw new Error('Complete surname family changed; review new competing names')
    if (!same(sourcePins(beforeFamily, baseline.index), p.sourceDefinitions) || !same(sourcePins(currentFamily, index), p.sourceDefinitions)) throw new Error('Surname family source IDs or definitions changed')
  }
  return payload.decisions.map(({ employer, names, preferredName, decision, note }) => ({ employer, names, preferredName, decision, note }))
}

/** Generate only from the exact11 root-approved regressions in the pinned graph. */
export const createBaselineLikelyConnections = (rows, index, baseline, root) => {
  const files = [BASELINE_LIKELY_INPUTS.graphPath, BASELINE_LIKELY_INPUTS.repeatPath, `${area}/baseline-people-index.json.gzip`]
  const inputs = files.map((path) => ({ path, sha256: sha(readFileSync(resolve(root, path))) }))
  const graph = JSON.parse(gunzipSync(readFileSync(resolve(root, BASELINE_LIKELY_INPUTS.graphPath))))
  const decisions = BASELINE_LIKELY_PAIRS.map(([aliasKey, targetKey]) => {
    const matches = graph.groups.flatMap(([slug, key, targetName, aliases]) => slug === employer && key === targetKey
      ? aliases.filter((a) => a[0] === aliasKey).map((a) => ({ targetName, aliasName: a[1], status: a[2], reason: a[3] })) : [])
    if (matches.length !== 1 || matches[0].status !== 'likely') throw new Error('Approved pair absent from pinned baseline graph')
    const old = matches[0], surname = aliasKey.split('|')[0]
    const family = histories(baseline.rows, baseline.index, employer, surname)
    return { employer, names: [old.aliasName, old.targetName], preferredName: old.targetName, decision: 'likely',
      note: `Retain the previously published likely connection as an assumption while both complete name histories and the entire employer surname family remain unchanged. This is no new identity evidence or verified claim. Original qualification: ${old.reason}`,
      proof: { aliasKey, targetKey, surname, oldStatus: 'likely', oldReason: old.reason, confidenceUpgradeAllowed: false, identityEstablished: false,
        alias: historyPin(histories(baseline.rows, baseline.index, employer, surname, aliasKey), baseline.index),
        target: historyPin(histories(baseline.rows, baseline.index, employer, surname, targetKey), baseline.index),
        family: historyPin(family, baseline.index), sourceDefinitions: sourcePins(family, baseline.index) } }
  })
  const payload = { schemaVersion: 1, scope: 'preserve-existing-likely-only', authorization: 'root-approved-existing-likely-preservation', reviewedOn: '2026-11-02',
    independentReview: 'source_translink independently found unchanged original PHSA observations and no new temporal, pay, title or surname-family contradiction. Root authorized retaining these11 already-published assumptions at likely confidence only.',
    inputs, decisions }
  validateBaselineLikelyConnections(payload, rows, index, baseline, root)
  return payload
}
