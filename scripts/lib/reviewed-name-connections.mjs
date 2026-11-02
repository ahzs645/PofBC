import { createHash } from 'node:crypto'
import { nameOnly, personKey } from '../../src/salaries/people.js'

const hash = (value) => createHash('sha256').update(JSON.stringify(value)).digest('hex')
const stableRow = (row, index) => [...row.slice(0, 4), index.employers[row[4]][3], index.years[row[5]], row[6], row[7] ?? null]
export const nameRecordFingerprint = (row, index) => hash(stableRow(row, index))
export const nameRowsFingerprint = (rows, index) => hash(rows.map((row) => nameRecordFingerprint(row, index)).sort())
const compiled = (source) => source?.sourceKind === 'compiled' || source?.scope === 'compiled-unverified'
const signature = (row, years) => JSON.stringify([row[4], years[row[5]].slice(0, 4), Math.round(row[2] * 100), row[3] == null ? null : Math.round(row[3] * 100)])

/** Revalidate every adopted source spelling before a rebuild can use its reviewed alias. */
export const validateReviewedNameConnections = (payload, rows, index) => {
  if (payload.schemaVersion !== 1 || !Array.isArray(payload.decisions)) throw new Error('Invalid source-reviewed name connections')
  const employers = new Map(index.employers.map((entry, at) => [entry[3], at]))
  const relevantEmployers = new Set(payload.decisions.map((entry) => employers.get(entry.employer)))
  const wanted = new Set(payload.decisions.flatMap((entry) => entry.names.map((name) => `${employers.get(entry.employer)}|${personKey(nameOnly(name))}`)))
  const byName = new Map()
  const byHash = new Map()
  const officialByMoney = new Map()
  for (const row of rows) {
    if (!relevantEmployers.has(row[4])) continue
    const key = `${row[4]}|${personKey(nameOnly(row[0]))}`
    if (wanted.has(key)) {
      if (!byName.has(key)) byName.set(key, [])
      byName.get(key).push(row)
      byHash.set(nameRecordFingerprint(row, index), row)
    }
    const source = index.sources[row[6]]
    if (!compiled(source) && source?.url && source.sha256) {
      const monetaryKey = signature(row, index.years)
      if (!officialByMoney.has(monetaryKey)) officialByMoney.set(monetaryKey, new Set())
      officialByMoney.get(monetaryKey).add(key)
    }
  }
  const seen = new Set()
  for (const entry of payload.decisions) {
    if (entry.decision !== 'verified' || entry.names?.length !== 2 || !entry.evidence?.length || !entry.proof?.witnesses?.length) throw new Error('Incomplete reviewed name evidence')
    const at = employers.get(entry.employer)
    if (at === undefined) throw new Error('Reviewed employer is absent')
    const sourceSpelling = entry.proof.kind === 'rendered-source-spelling'
    if (entry.proof.kind && !sourceSpelling) throw new Error('Unknown reviewed name proof')
    const from = `${at}|${sourceSpelling ? entry.proof.aliasNameKey : entry.proof.compiledNameKey}`
    const target = `${at}|${personKey(nameOnly(entry.preferredName))}`
    const supportedNames = sourceSpelling ? [from, target] : [target]
    if (from === target || !entry.names.some((name) => `${at}|${personKey(nameOnly(name))}` === from)
      || !entry.names.some((name) => `${at}|${personKey(nameOnly(name))}` === target)) throw new Error('Reviewed names disagree with their proof')
    if (seen.has(from)) throw new Error('A source spelling has conflicting reviewed targets')
    seen.add(from)
    const originals = byName.get(from) ?? []
    if (!originals.length || (!sourceSpelling && originals.some((row) => !compiled(index.sources[row[6]])))
      || nameRowsFingerprint(originals, index) !== (sourceSpelling ? entry.proof.aliasRowsSha256 : entry.proof.compiledRowsSha256)) throw new Error('Compiled or source alias observations changed; review again')
    const witnesses = entry.proof.witnesses.map((evidence) => {
      const row = byHash.get(evidence.rowSha256)
      const source = index.sources[evidence.sourceId]
      if (!row || compiled(source) || !source?.url || source.sha256 !== evidence.pdfSha256
        || row[6] !== evidence.sourceId || row[7] !== evidence.pdfPage
        || !supportedNames.includes(`${row[4]}|${personKey(nameOnly(row[0]))}`)
        || (sourceSpelling && evidence.printedNameKey !== personKey(nameOnly(entry.preferredName)))
        || !entry.evidence.some((link) => link.sourceId === evidence.sourceId && link.pdfPage === evidence.pdfPage)) throw new Error('Original name witness changed; review again')
      return row
    })
    if (sourceSpelling) {
      const officialAliases = originals.filter((row) => !compiled(index.sources[row[6]]))
      if (!officialAliases.length || !witnesses.some((row) => `${row[4]}|${personKey(nameOnly(row[0]))}` === target)
        || officialAliases.some((row) => !witnesses.some((witness) => nameRecordFingerprint(witness, index) === nameRecordFingerprint(row, index)))) throw new Error('Every official alias row requires its own rendered spelling review and an existing target name')
    }
    for (const row of originals) {
      if (sourceSpelling && !compiled(index.sources[row[6]])) continue
      const key = signature(row, index.years)
      const names = officialByMoney.get(key)
      if (row[3] == null || !names || names.size !== 1 || !supportedNames.some((name) => names.has(name))
        || !witnesses.some((witness) => signature(witness, index.years) === key)) throw new Error('The source row no longer uniquely supports the spelling correction')
    }
  }
  return payload.decisions
}
