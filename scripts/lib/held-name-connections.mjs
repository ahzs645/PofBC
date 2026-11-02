import { readFileSync } from 'node:fs'
import { resolve, relative, sep } from 'node:path'
import { createHash } from 'node:crypto'
import { nameOnly, nameParts, personKey } from '../../src/salaries/people.js'
import { isCadPerson, personAnnotation } from '../../src/salaries/recordAnnotations.js'
import { nameRecordFingerprint, nameRowsFingerprint } from './reviewed-name-connections.mjs'

const sha = (value) => createHash('sha256').update(value).digest('hex')
const flat = (name) => String(name).toLowerCase().replace(/[^a-z]/g, '')
const compiled = (source) => source?.sourceKind === 'compiled' || source?.scope === 'compiled-unverified'
const payKey = (row, index) => `${row[4]}|${index.years[row[5]].slice(0, 4)}|${Math.round(row[2] * 100)}`

/** Explicit review modes keep a name correction, an expense value and a qualified inference separate. */
export const validateHeldNameConnections = (payload, rows, index, root) => {
  if (payload.schemaVersion !== 1 || !Array.isArray(payload.decisions)) throw new Error('Invalid completed name review')
  for (const pin of payload.inputs ?? []) {
    const path = resolve(root, pin.path)
    if (relative(root, path).startsWith(`..${sep}`) || sha(readFileSync(path)) !== pin.sha256) throw new Error(`Name review evidence changed: ${pin.path}`)
  }
  const pinned = new Set((payload.inputs ?? []).map((pin) => pin.path))
  const receipt = (ref) => {
    if (!pinned.has(ref.path)) throw new Error('A review receipt must be pinned')
    const value = JSON.parse(readFileSync(resolve(root, ref.path), 'utf8'))
    const found = (Array.isArray(value) ? value : value.decisions ?? []).find((row) => row.id === ref.id)
    if (!found) throw new Error('Missing individual review receipt')
    return found
  }
  const employers = new Map(index.employers.map((e, at) => [e[3], at]))
  const wanted = new Set(payload.decisions.flatMap((e) => e.names.map((n) => `${employers.get(e.employer)}|${personKey(nameOnly(n))}`)))
  const byName = new Map(), byHash = new Map(), payNames = new Map(), neededPay = new Set()
  for (const e of payload.decisions) for (const w of e.proof.witnesses ?? []) neededPay.add(`${employers.get(e.employer)}|${w.periodPrefix}|${w.payCents}`)
  for (const row of rows) {
    const key = `${row[4]}|${personKey(nameOnly(row[0]))}`
    if (wanted.has(key)) {
      if (!byName.has(key)) byName.set(key, [])
      byName.get(key).push(row); byHash.set(nameRecordFingerprint(row, index), row)
    }
    const pk = payKey(row, index)
    if (neededPay.has(pk) && !compiled(index.sources[row[6]])) {
      if (!payNames.has(pk)) payNames.set(pk, new Set())
      payNames.get(pk).add(key)
    }
  }
  for (const e of payload.decisions) {
    if (!['verified', 'likely'].includes(e.decision) || e.names.length !== 2 || !e.note || !e.evidence?.length) throw new Error('Incomplete continued identity decision')
    const at = employers.get(e.employer)
    if (at == null) throw new Error('Missing reviewed employer')
    const keys = e.names.map((n) => `${at}|${personKey(nameOnly(n))}`)
    for (const group of e.proof.observations) {
      const rs = byName.get(`${at}|${group.nameKey}`) ?? []
      if (!rs.length || nameRowsFingerprint(rs, index) !== group.rowsSha256) throw new Error('Reviewed name observations changed')
    }
    if (e.proof.observations.length !== 2 || !keys.every((k) => e.proof.observations.some((o) => `${at}|${o.nameKey}` === k))) throw new Error('Every reviewed name needs its complete observation fingerprint')
    if (e.displaySpelling && !(byName.get(`${at}|${personKey(nameOnly(e.displaySpelling))}`) ?? []).some((r) => r[0] === e.displaySpelling)) throw new Error('Preferred spelling was not published')
    const method = e.proof.method
    if (method === 'professional-identity' || method === 'conservative-inference') {
      if (!e.proof.receipts?.length) throw new Error('A professional review needs pinned primary evidence')
      if (method === 'conservative-inference' && e.decision !== 'likely') throw new Error('An assumption cannot be verified')
      const individual = e.proof.receipts.map(receipt).find((r) => r.id === e.candidateId
        && r.employer === e.employer && JSON.stringify(r.names) === JSON.stringify(e.names))
      if (!individual) throw new Error('The receipt does not describe this name pair')
      if (method === 'conservative-inference' && individual.assessment !== 'supported-likely-source-inference') throw new Error('This pair is blocked from continuity inference')
      if (method === 'professional-identity' && (individual.decision !== e.decision || individual.note !== e.note
        || individual.canonicalName !== e.canonicalName || individual.currencyAnnotationId !== e.proof.currencyAnnotationId
        || JSON.stringify(individual.evidence) !== JSON.stringify(e.evidence))) throw new Error('The adopted professional decision disagrees with its receipt')
      if (e.canonicalName && (method !== 'professional-identity' || e.decision !== 'verified')) throw new Error('A reviewed full name requires verified professional evidence')
      if (e.proof.currencyAnnotationId && !keys.flatMap((k) => byName.get(k) ?? []).some((r) => personAnnotation(r, index)?.id === e.proof.currencyAnnotationId)) throw new Error('Required record-level currency treatment is missing')
      continue
    }
    if (e.canonicalName) throw new Error('A spelling correction cannot invent a disclosed full name')
    if (!['unique-remuneration-row', 'surname-initial-separator'].includes(method)) throw new Error('Unknown name review method')
    const witnesses = (e.proof.witnesses ?? []).map((w) => {
      const row = byHash.get(w.rowSha256), source = index.sources[w.sourceId]
      if (!row || compiled(source) || source?.sha256 !== w.pdfSha256 || row[6] !== w.sourceId || row[7] !== w.pdfPage
        || !e.evidence.some((v) => v.sourceId === w.sourceId && v.pdfPage === w.pdfPage) || !isCadPerson(row, index)
        || payKey(row, index) !== `${at}|${w.periodPrefix}|${w.payCents}`) throw new Error('Reviewed original remuneration witness changed')
      return row
    })
    if (!witnesses.length) throw new Error('A printed spelling review needs an original row')
    if (method === 'surname-initial-separator') {
      const [printed, formatted] = e.names
      if (e.decision !== 'verified' || printed.includes(',') || !formatted.includes(',') || flat(printed) !== flat(formatted)
        || !nameParts(formatted).given.every((part) => part.length === 1)) throw new Error('A separator review cannot infer a full given name or change letters')
      continue
    }
    const [aliasKey, targetKey] = keys
    const originals = byName.get(aliasKey)
    if (!originals.every((r) => compiled(index.sources[r[6]]))) throw new Error('A compiled spelling review includes an official alias; inspect that original separately')
    for (const row of originals) {
      const pk = payKey(row, index), names = payNames.get(pk)
      const matches = witnesses.filter((w) => payKey(w, index) === pk && `${at}|${personKey(nameOnly(w[0]))}` === targetKey)
      if (!isCadPerson(row, index) || names?.size !== 1 || !names.has(targetKey) || !matches.length) throw new Error('The remuneration no longer uniquely identifies the reviewed source name')
      if (!matches.some((w) => (row[3] === w[3] && row[3] != null) || (row[3] === 0 && w[3] == null))) throw new Error('An unreviewed expense discrepancy cannot support this spelling rule')
      const left = nameParts(e.names[0]), right = nameParts(e.names[1])
      if (left.given[0]?.[0] !== right.given[0]?.[0]) {
        if (e.decision !== 'likely' || !row[1] || !matches.some((w) => w[1]?.toLowerCase() === row[1].toLowerCase())) throw new Error('Conflicting initials need a qualified source-copy inference and the same position')
      }
    }
  }
  return payload.decisions
}
