// Reviewed joins for compiled copies of an employer report's record under another spelling
// (research/salaries/name-links/repeat-reviewed.json). Each decision names the compiled spelling, the
// report's spelling and the records that witness it; a rebuild re-checks every witness against the
// published rows, so a decision cannot outlive the data it was read from.
import { nameOnly, personKey } from '../../src/salaries/people.js'

const compiled = (source) => source?.sourceKind === 'compiled' || source?.scope === 'compiled-unverified'

/**
 * `rows` are the people index's ([name, position, pay, expenses, employer, year, source, page]).
 * Returns the decisions in reviewed.json's shape; throws if any no longer holds:
 *   - in each witnessed year, the compiled spelling has a compiled record and the report's spelling
 *     a record from the witnessed source, both with the witnessed pay and expenses (spellings are
 *     compared as name keys, as the joins are);
 *   - that primary record is the employer's only one with that pay and expenses that year;
 *   - the employer never printed the compiled spelling itself.
 */
export const validateRepeatNameConnections = (payload, rows, index) => {
  if (payload.schemaVersion !== 1 || !Array.isArray(payload.decisions)) throw new Error('Invalid repeat-reviewed name connections')
  const employers = new Map(index.employers.map((entry, at) => [entry[3], at]))
  const years = new Map(index.years.map((label, at) => [label, at]))
  const relevant = new Set(payload.decisions.map((entry) => employers.get(entry.employer)))
  const byName = new Map()
  const primaryByMoney = new Map()
  for (const row of rows) {
    if (!row[0] || !relevant.has(row[4])) continue
    const key = `${row[4]}|${personKey(nameOnly(row[0]))}`
    if (!byName.has(key)) byName.set(key, [])
    byName.get(key).push(row)
    const source = index.sources[row[6]]
    if (!compiled(source) && source?.url && source.sha256 && row[3] != null) {
      const money = `${row[4]}|${row[5]}|${row[2]}|${row[3]}`
      primaryByMoney.set(money, (primaryByMoney.get(money) ?? 0) + 1)
    }
  }
  const seen = new Map()
  for (const entry of payload.decisions) {
    const at = employers.get(entry.employer)
    const [copy, report] = entry.names ?? []
    if (at === undefined || entry.decision !== 'verified' || entry.preferredName !== report || !entry.witnesses?.length) throw new Error(`Incomplete repeat review: ${JSON.stringify(entry.names)}`)
    const copyKey = `${at}|${personKey(nameOnly(copy))}`
    if (seen.has(copyKey) && seen.get(copyKey) !== report) throw new Error(`A compiled spelling has conflicting reviewed targets: ${copy}`)
    seen.set(copyKey, report)
    const copyRows = byName.get(copyKey) ?? []
    if (copyRows.some((row) => !compiled(index.sources[row[6]]))) throw new Error(`The employer printed the compiled spelling itself: ${copy}`)
    const reportRows = byName.get(`${at}|${personKey(nameOnly(report))}`) ?? []
    for (const witness of entry.witnesses) {
      const year = years.get(witness.year)
      const same = (row) => row[5] === year && row[2] === witness.pay && row[3] === witness.expenses
      if (!copyRows.some((row) => compiled(index.sources[row[6]]) && same(row))) throw new Error(`No compiled record for ${copy} in ${witness.year}`)
      if (!reportRows.some((row) => row[6] === witness.sourceId && same(row))) throw new Error(`No report record for ${report} in ${witness.year}`)
      if (primaryByMoney.get(`${at}|${year}|${witness.pay}|${witness.expenses}`) !== 1) throw new Error(`The report record for ${report} in ${witness.year} is not unique`)
    }
  }
  return payload.decisions.map(({ employer, names, preferredName, decision, note, evidence }) => ({ employer, names, preferredName, decision, note, ...(evidence?.length ? { evidence } : {}) }))
}
