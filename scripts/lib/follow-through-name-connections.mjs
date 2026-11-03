import { readFileSync } from 'node:fs'
import { resolve, relative, sep } from 'node:path'
import { gunzipSync } from 'node:zlib'
import { createHash } from 'node:crypto'
import { nameOnly, personKey } from '../../src/salaries/people.js'
import { isCadPerson } from '../../src/salaries/recordAnnotations.js'
import { nameRecordFingerprint, nameRowsFingerprint } from './reviewed-name-connections.mjs'

const sha = (bytes) => createHash('sha256').update(bytes).digest('hex')
const compiled = (s) => s?.sourceKind === 'compiled' || s?.scope === 'compiled-unverified'
const keyOf = (row, index) => `${index.employers[row[4]]?.[3]}|${personKey(nameOnly(row[0]))}`
const cents = (n) => n == null ? null : Math.round(n * 100)
const validSha = (s) => typeof s === 'string' && /^[a-f0-9]{64}$/.test(s)
const equal = (a, b) => JSON.stringify(a) === JSON.stringify(b)
const sourceIdentity = (s) => [s?.id ?? null, s?.url ?? null, s?.sha256 ?? null, s?.dataSha256 ?? null,
  s?.year ?? null, s?.periodType ?? null, s?.periodStart ?? null, s?.periodEnd ?? null,
  s?.sourceKind ?? null, s?.scope ?? null, s?.currency ?? 'CAD']
export const followThroughSourceFingerprint = (s) => sha(JSON.stringify(sourceIdentity(s)))

/** New source-copy reviews pin both complete live name histories, both original cohorts,
 * the exact compiled/official rows, and the individually inspected source pixels.
 * Monetary witnesses support this source-copy spelling only; fiscal labels remain distinct.
 */
export const validateFollowThroughNameReview = (payload, rows, index, root, { readInput = (path) => readFileSync(resolve(root, path)) } = {}) => {
  if (payload?.schemaVersion !== 1 || payload.reviewKind !== 'manual-source-copy-spelling'
    || !Array.isArray(payload.decisions) || !Array.isArray(payload.inputs)) throw new Error('Invalid follow-through name review')
  const pinned = new Map()
  for (const pin of payload.inputs) {
    const path = resolve(root, pin.path)
    if (typeof pin.path !== 'string' || relative(root, path).startsWith(`..${sep}`) || !relative(root, path)
      || !validSha(pin.sha256) || pinned.has(pin.path)) throw new Error('Invalid name review input pin')
    const bytes = readInput(pin.path)
    if (sha(bytes) !== pin.sha256) throw new Error(`Name review input changed: ${pin.path}`)
    pinned.set(pin.path, bytes)
  }
  const input = (path) => {
    if (!pinned.has(path)) throw new Error(`Name review evidence is not pinned: ${path}`)
    return pinned.get(path)
  }
  const parsedInputs = new Map()
  const inputJson = (path) => {
    if (!parsedInputs.has(path)) parsedInputs.set(path, JSON.parse((path.endsWith('.gzip') ? gunzipSync(input(path)) : input(path)).toString('utf8')))
    return parsedInputs.get(path)
  }
  const wantedEmployers = new Set(payload.decisions.map((e) => e.employer))
  const wantedNames = new Set(payload.decisions.flatMap((e) => e.names.map((n) => `${e.employer}|${personKey(nameOnly(n))}`)))
  const byName = new Map(), byHash = new Map(), employerRows = new Map()
  for (const row of rows) {
    const slug = index.employers[row[4]]?.[3]
    if (!wantedEmployers.has(slug)) continue
    if (!employerRows.has(slug)) employerRows.set(slug, [])
    employerRows.get(slug).push(row)
    const k = keyOf(row, index)
    if (wantedNames.has(k)) {
      if (!byName.has(k)) byName.set(k, [])
      byName.get(k).push(row)
      const h = nameRecordFingerprint(row, index)
      if (!byHash.has(h)) byHash.set(h, [])
      byHash.get(h).push(row)
    }
  }
  const seen = new Set(), candidateIds = new Set()
  for (const e of payload.decisions) {
    const p = e.proof
    if (e.decision !== 'verified' || e.names?.length !== 2 || !e.note || !e.evidence?.length
      || e.canonicalName || !e.preferredName || !e.names.includes(e.preferredName)
      || p?.kind !== 'manual-source-copy-spelling' || p.reviewer !== 'root' || p.individualCropReviewed !== true
      || p.retainAllObservations !== true || p.redateCompiledObservations !== false) throw new Error('Incomplete individual source-copy review')
    const aliasKey = `${e.employer}|${p.aliasNameKey}`, targetKey = `${e.employer}|${p.targetNameKey}`
    if (aliasKey === targetKey || seen.has(aliasKey)
      || !equal(e.names.map((n) => personKey(nameOnly(n))), [p.aliasNameKey, p.targetNameKey])
      || personKey(nameOnly(e.preferredName)) !== p.targetNameKey) throw new Error('Conflicting source-copy names or targets')
    seen.add(aliasKey)
    const aliasRows = byName.get(aliasKey) ?? [], targetRows = byName.get(targetKey) ?? []
    if (!aliasRows.length || !targetRows.length || p.observations?.length !== 2) throw new Error('Both live name observation histories are required')
    for (const [nameKey, rs] of [[p.aliasNameKey, aliasRows], [p.targetNameKey, targetRows]]) {
      const pin = p.observations.find((o) => o.nameKey === nameKey)
      if (!pin || pin.rowCount !== rs.length || nameRowsFingerprint(rs, index) !== pin.rowsSha256) throw new Error('Live alias or target observations changed; review every new observation')
    }
    // Source changes in any pinned live name history invalidate a review too.
    const sourceIds = [...new Set([...aliasRows, ...targetRows].map((r) => r[6]))].sort()
    if (!equal(sourceIds, (p.liveSources ?? []).map((s) => s.sourceId).sort())) throw new Error('Live name source set changed')
    for (const pin of p.liveSources) {
      if (followThroughSourceFingerprint(index.sources[pin.sourceId]) !== pin.sourceSha256) throw new Error('Live name source definition changed')
    }
    const original = p.official, retained = p.compiled
    const source = index.sources[original?.sourceId], compiledSource = index.sources[retained?.sourceId]
    if (!source || compiled(source) || !source.url?.startsWith('https://') || !validSha(source.sha256) || !validSha(source.dataSha256)
      || source.sha256 !== original.pdfSha256 || source.dataSha256 !== original.dataSha256 || source.url !== original.sourceUrl
      || source.year !== original.year || source.periodType !== original.periodType || source.periodStart !== original.periodStart || source.periodEnd !== original.periodEnd
      || !compiled(compiledSource) || compiledSource.sha256 !== retained.sourceSha256 || original.currency !== 'CAD' || retained.currency !== 'CAD') throw new Error('Official or compiled source witness changed')
    if (p.periodReview?.officialYear !== original.year || p.periodReview?.compiledYear !== retained.year
      || p.periodReview.compiledLabelVerified !== false || !p.periodReview.reason?.trim()) throw new Error('Source-copy period qualification changed')
    const witnessRow = (pin, expectedKey) => {
      const found = byHash.get(pin.rowSha256) ?? []
      if (found.length !== 1 || keyOf(found[0], index) !== expectedKey || found[0][6] !== pin.sourceId
        || index.years[found[0][5]] !== pin.year || (found[0][7] ?? null) !== pin.pdfPage
        || found[0][0] !== pin.publishedName || !isCadPerson(found[0], index)) throw new Error('Exact source row, page, year or currency witness changed')
      return found[0]
    }
    const officialRow = witnessRow(original, targetKey), compiledRow = witnessRow(retained, aliasKey)
    if (officialRow[0] !== e.preferredName || !aliasRows.every((r) => compiled(index.sources[r[6]]))) throw new Error('A source-copy alias includes unreviewed official observations')
    const cohort = employerRows.get(e.employer) ?? []
    const officialCohort = cohort.filter((r) => r[6] === original.sourceId && index.years[r[5]] === original.year)
    const compiledCohort = cohort.filter((r) => compiled(index.sources[r[6]]) && index.years[r[5]] === retained.year)
    for (const [rs, pin] of [[officialCohort, p.cohorts?.official], [compiledCohort, p.cohorts?.compiled]]) {
      if (!pin || pin.rowCount !== rs.length || nameRowsFingerprint(rs, index) !== pin.rowsSha256) throw new Error('Reviewed complete source cohort changed')
    }
    const m = p.financialWitness
    const hasBothExpenses = officialRow[3] != null && compiledRow[3] != null
    const mode = hasBothExpenses ? 'unique-remuneration-and-expenses' : 'unique-remuneration-only-missing-expense'
    if (m?.mode !== mode || cents(officialRow[2]) !== m.payCents || cents(compiledRow[2]) !== m.payCents
      || cents(officialRow[3]) !== m.officialExpensesCents || cents(compiledRow[3]) !== m.compiledExpensesCents
      || (hasBothExpenses && officialRow[3] !== compiledRow[3]) || m.nullExpensesEqualZero !== false) throw new Error('Financial witness changed; missing expenses are not zero')
    const matching = (rs) => rs.filter((r) => isCadPerson(r, index) && cents(r[2]) === m.payCents
      && (!hasBothExpenses || cents(r[3]) === m.officialExpensesCents))
    const left = matching(compiledCohort), right = matching(officialCohort)
    if (left.length !== 1 || right.length !== 1 || m.compiledOccurrenceCount !== 1 || m.officialOccurrenceCount !== 1
      || nameRecordFingerprint(left[0], index) !== retained.rowSha256 || nameRecordFingerprint(right[0], index) !== original.rowSha256) throw new Error('Financial witness is no longer unique in both complete cohorts')
    // All alias history is pinned above, but no unmatched compiled alias occurrence can be swept in.
    if (aliasRows.some((r) => nameRecordFingerprint(r, index) !== retained.rowSha256)) throw new Error('Additional alias observations lack individual source-copy witnesses')
    const crop = p.crop
    if (!crop || crop.pdfPage !== original.pdfPage || crop.pdfSha256 !== original.pdfSha256 || crop.printedName !== e.preferredName
      || !equal(crop.rowSha256, original.rowSha256) || !Array.isArray(crop.bboxPoints) || crop.bboxPoints.length !== 4
      || !crop.bboxPoints.every(Number.isFinite) || crop.bboxPoints[0] >= crop.bboxPoints[2] || crop.bboxPoints[1] >= crop.bboxPoints[3]
      || sha(input(crop.path)) !== crop.sha256 || sha(input(crop.fullPagePath)) !== crop.fullPageSha256
      || sha(input(original.normalizedPath)) !== original.dataSha256) throw new Error('Reviewed source crop, physical page or normalized data changed')
    const receipt = inputJson(crop.receiptPath).receipts.find((r) => r.originalSpelling === e.preferredName && r.compiledSpelling === e.names[0])
    if (!receipt || receipt.pdfPage !== crop.pdfPage || receipt.pdfSha256 !== crop.pdfSha256 || receipt.cropSha256 !== crop.sha256
      || receipt.fullPageSha256 !== crop.fullPageSha256 || !equal(receipt.bboxPoints, crop.bboxPoints)) throw new Error('Individual source crop receipt changed')
    const requiredNative = Boolean(receipt.earlierNativeSupport)
    if ((requiredNative && (p.requiresEarlierNativeSpellingSupport !== true || p.supportingOriginals?.length !== 1))
      || (p.requiresEarlierNativeSpellingSupport === true && !p.supportingOriginals?.length)) throw new Error('Required earlier native spelling support is missing')
    for (const support of p.supportingOriginals ?? []) {
      const sr = witnessRow(support, targetKey), ss = index.sources[support.sourceId]
      const native = receipt.earlierNativeSupport
      if (!native || compiled(ss) || ss.sha256 !== support.pdfSha256 || ss.dataSha256 !== support.dataSha256
        || ss.url !== support.sourceUrl || ss.year !== support.year || ss.periodType !== support.periodType
        || ss.periodStart !== support.periodStart || ss.periodEnd !== support.periodEnd || support.currency !== 'CAD'
        || support.publishedName !== e.preferredName || support.sourceId !== native.sourceId
        || support.pdfPage !== native.physicalPdfPage || support.pdfSha256 !== native.pdfSha256 || support.dataSha256 !== native.dataSha256
        || sha(input(support.normalizedPath)) !== support.dataSha256 || sha(input(support.cropPath)) !== support.cropSha256
        || support.cropSha256 !== native.crop?.sha256 || !equal(support.bboxPoints, native.crop?.bboxPoints)
        || !equal(support.nativeWords, native.nativeWordEvidence)) throw new Error('Earlier native spelling source, crop or page changed')
      const packedSupport = inputJson(support.normalizedPath)
      const supportRows = Array.isArray(packedSupport) ? packedSupport : packedSupport.rows
      const supportRow = [e.employer, sr[0], sr[1], sr[2], sr[3], sr[7]]
      if (!Array.isArray(supportRows) || supportRows.filter((r) => equal(r, supportRow)).length !== 1) throw new Error('Earlier native spelling row changed')
    }
    const packed = inputJson(original.normalizedPath)
    const normalized = Array.isArray(packed) ? packed : packed.rows
    const nativeRow = [e.employer, officialRow[0], officialRow[1], officialRow[2], officialRow[3], officialRow[7]]
    if (!Array.isArray(normalized) || normalized.length !== officialCohort.length || normalized.filter((r) => equal(r, nativeRow)).length !== 1) throw new Error('Original normalized source row is absent or ambiguous')
    const baseline = inputJson(retained.normalizedPath)
    if (sha(input(retained.normalizedPath)) !== retained.sourceSha256) throw new Error('Compiled source baseline changed')
    const compiledEmployer = baseline.employers?.find((r) => r.slug === e.employer)
    const baseRows = compiledEmployer?.rows?.filter((r) => baseline.years[r[4]] === retained.year) ?? []
    if (baseRows.length !== compiledCohort.length || baseRows.filter((r) => equal(r.slice(0, 4), compiledRow.slice(0, 4))).length !== 1) throw new Error('Exact retained compiled source observation changed')
    if (!e.evidence.some((r) => r.sourceId === original.sourceId && r.pdfPage === original.pdfPage
      && r.url === `${source.url}#page=${original.pdfPage}`)) throw new Error('Published source evidence disagrees with witness')
    if (e.queueMembership === 'original-3173') {
      if (typeof e.candidateId !== 'string' || candidateIds.has(e.candidateId)) throw new Error('Invalid original candidate id')
      candidateIds.add(e.candidateId)
      const old = inputJson(p.originalOutcomesPath)
      const matched = old.rows.filter((r) => r.candidate_id === e.candidateId && r.employer === e.employer)
      if (old.rowCount !== 3173 || old.rows.length !== 3173 || matched.length !== 1
        || !equal([matched[0].name_a, matched[0].name_b].map((n) => personKey(nameOnly(n))).sort(), [p.aliasNameKey, p.targetNameKey].sort())) throw new Error('Original3173 candidate membership changed')
    } else if (e.queueMembership !== 'additional-source-copy' || e.candidateId != null) throw new Error('Additional source-copy lead must stay outside the original queue')
  }
  return payload.decisions
}
