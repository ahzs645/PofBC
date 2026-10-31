import test from 'node:test'
import assert from 'node:assert/strict'
import { mkdtempSync, mkdirSync, writeFileSync, readFileSync, rmSync } from 'node:fs'
import { tmpdir } from 'node:os'
import { join, resolve } from 'node:path'
import { gzipSync, gunzipSync } from 'node:zlib'
import { spawnSync } from 'node:child_process'
import { csvRows, money, sumMoney, median, duplicateStats, repeatedCandidates, sha256, validateReplacementScopes, yearSlug, reportingPeriodType, applyCompiledReplacements, applyTravelJoinCorrections } from './lib/salary-data.mjs'
import { sourceCatalog, sourceLeadsFor, hasLocatedSource } from './lib/salary-sources.mjs'
import { employerSector, employerSlug, canonicalSlug } from './lib/salary-employers.mjs'

const row = (name, pay = 100000.01, year = '2017/18') => ({ slug: 'bc-hydro', year, name, position: null, pay, expenses: null })
test('municipalities and Metro Vancouver are local government, not the provincial Government sector', () => {
  assert.equal(canonicalSlug('district-of-mission'), 'city-of-mission')
  assert.equal(canonicalSlug('district-of-delta'), 'city-of-delta')
  assert.equal(canonicalSlug('township-of-langley'), 'langley-township')
  assert.equal(canonicalSlug('bowen-island-municipality'), 'bowen-island')
  for (const slug of ['city-of-vancouver', 'city-of-prince-george', 'district-of-saanich', 'village-of-anmore', 'bowen-island',
    'langley-township', 'langley-city', 'metro-vancouver', employerSlug('District of Delta'), employerSlug('Township of Langley')]) {
    assert.equal(employerSector(slug, 'Government'), 'Municipalities', slug)
  }
  assert.equal(employerSector('public-service', 'Government'), 'Government')
  assert.equal(employerSector('vancouver-police', 'Municipal police'), 'Municipal police')
  assert.equal(employerSector('vancouver-school-district', 'School districts'), 'School districts')
  assert.equal(employerSector('north-vancouver-school-district', 'School districts'), 'School districts')
})
test('calendar and fiscal reporting periods retain distinct labels and output paths', () => {
  assert.equal(yearSlug('2020'), '2020')
  assert.equal(yearSlug('2020/21'), '2020-21')
  assert.equal(reportingPeriodType('2020'), 'calendar')
  assert.equal(reportingPeriodType('2020/21'), 'fiscal')
  assert.throws(() => yearSlug('2020/22'), /Invalid disclosure year/)
  assert.throws(() => yearSlug('2020-21'), /Invalid disclosure year/)
})
test('a pinned calendar correction preserves council and fails closed when source evidence changes', () => {
  const employee = { ...row('Employee, A', 100000, '2020/21'), sourceId: 'compiled' }
  const mayor = { ...row('Mayor, B', 150000, '2020/21'), position: 'Mayor', sourceId: 'compiled' }
  const original = [employee, mayor]
  const officialHash = sha256('reviewed official source fixture')
  const rule = { employerSlug: 'bc-hydro', compiledYear: '2020/21', replacementYear: '2020', sourceIds: ['official'],
    sourceDataSha256: { official: officialHash },
    expectedRows: 1, expectedRetainedRows: 1, selectedRowsSha256: sha256(JSON.stringify([[employee.name, employee.position, employee.pay, employee.expenses]])),
    retainPositions: ['Mayor'], reason: 'Verified source calendar period and exact cohort comparison.',
    retainedSource: { id: 'compiled-council', scope: 'elected-officials' } }
  const sources = () => ({ compiled: { scope: 'compiled-unverified', sourceKind: 'compiled' }, official: { scope: 'employee-remuneration', dataSha256: officialHash } })
  const official = [{ ...employee, year: '2020', sourceId: 'official' }]
  const registry = sources()
  const result = applyCompiledReplacements(original, official, registry, [rule])
  assert.equal(result.rows.length, 1)
  assert.equal(result.rows[0].name, mayor.name)
  assert.equal(result.rows[0].year, '2020/21')
  assert.equal(registry['compiled-council'].sourceKind, 'compiled')
  assert.equal(registry['compiled-council'].periodType, 'unverified')
  assert.equal(result.corrections[0].correctedYear, '2020')
  assert.throws(() => applyCompiledReplacements(original, [], sources(), [rule]), /not imported/)
  assert.throws(() => applyCompiledReplacements([{ ...employee, pay: 100001 }, mayor], official, sources(), [rule]), /evidence no longer matches/)
  assert.throws(() => applyCompiledReplacements(original, official, sources(), [{ ...rule, retainPositions: [] }]), /evidence no longer matches/)
  assert.throws(() => applyCompiledReplacements(original, official, { ...sources(), official: { scope: 'executive-only', dataSha256: officialHash } }, [rule]), /partial disclosure/)
  assert.throws(() => applyCompiledReplacements(original, official, { ...sources(), official: { scope: 'employee-remuneration', dataSha256: sha256('changed source') } }, [rule]), /source fingerprint changed/)
  assert.throws(() => applyCompiledReplacements(original, official, sources(), [{ ...rule, sourceDataSha256: {} }]), /source fingerprint changed/)
})
test('a recovered cohort clears only an exactly reviewed ambiguous travel assignment', () => {
  const employee = { ...row('Example,Pat', 90000, '2017/18'), sourceId: 'employees', expenses: 16000 }
  const appointee = { ...row('EXAMPLE,PAT', 150000, '2017/18'), sourceId: 'appointees' }
  const decision = { employeeSourceId: 'employees', employerSlug: 'bc-hydro', year: '2017/18', name: 'Example,Pat', pay: 90000,
    previousExpenses: 16000, replacementExpenses: null, relatedOICSourceId: 'appointees', relatedOICName: 'EXAMPLE,PAT', relatedOICRemuneration: 150000,
    reason: 'Newly recovered schedule makes the disclosed name non-unique.' }
  const sources = { employees: { travelSource: { url: 'https://example.test/travel.csv' } }, appointees: {} }
  const result = applyTravelJoinCorrections([employee, appointee], sources, [decision])
  assert.equal(result.rows[0].expenses, null)
  assert.equal(result.rows[1].expenses, null)
  assert.equal(employee.expenses, 16000)
  assert.throws(() => applyTravelJoinCorrections([employee], sources, [decision]), /evidence no longer matches/)
  assert.throws(() => applyTravelJoinCorrections([employee, appointee], sources, [{ ...decision, previousExpenses: 16001 }]), /evidence no longer matches/)
})
test('money retains cents, distinguishes missing from zero, and permits published recoveries', () => {
  assert.equal(money('$100,000.01'), 100000.01)
  assert.equal(money('0'), 0)
  assert.equal(money('NA'), null)
  assert.equal(money(''), null)
  assert.equal(money('-5,110'), -5110)
  assert.throws(() => money('100000x'), /Invalid money/)
  assert.equal(sumMoney([0.1, 0.2]), 0.3)
  assert.equal(median([1.01, 1.02]), 1.02)
})
test('CSV rejects truncated quoted rows and keeps embedded delimiters', () => {
  assert.deepEqual([...csvRows('Name,Amount\r\n"Smith, A",100\n"line\nname",200')], [['Name', 'Amount'], ['Smith, A', '100'], ['line\nname', '200']])
  assert.throws(() => [...csvRows('Name\n"unterminated')], /Unclosed/)
})
test('repetition compares earlier populated years but remains review-only', () => {
  const old = Array.from({ length: 25 }, (_, at) => row(`Surname${at}, A`))
  const next = old.map((entry) => ({ ...entry, year: '2023/24' }))
  const result = repeatedCandidates([...old, ...next])
  assert.equal(result.length, 1)
  assert.equal(result[0].repeats, '2017/18')
  assert.equal(result[0].action, 'review-only')
  assert.equal(result[0].same, 25)
  assert.equal(next.length, 25)
})
test('repetition respects multiplicity and does not use anonymous rows as identity matches', () => {
  const old = Array.from({ length: 25 }, (_, at) => row(`Surname${at}, A`))
  const repeatsOneName = Array.from({ length: 25 }, () => row('Surname0, A', 100000.01, '2020/21'))
  assert.deepEqual(repeatedCandidates([...old, ...repeatsOneName]), [])
  assert.deepEqual(repeatedCandidates(Array.from({ length: 50 }, (_, at) => row(null, 100000, at < 25 ? '2017/18' : '2020/21'))), [])
  assert.deepEqual(repeatedCandidates([...old, ...old.map((entry) => ({ ...entry, pay: entry.pay + 0.01, year: '2020/21' }))]), [])
})
test('duplicate-looking rows are counted without deleting possible distinct people', () => {
  const rows = [row('Lee, A'), row('Lee, A'), row('Lee, B')]
  assert.deepEqual(duplicateStats(rows), { duplicateRows: 1, duplicateGroups: 1 })
  assert.equal(rows.length, 3)
})

const fixture = () => {
  const dir = mkdtempSync(join(tmpdir(), 'pofbc-salary-test-'))
  const research = join(dir, 'research'); mkdirSync(research)
  const baseline = { provenance: { description: 'Fixture compiled input' }, years: ['2017/18', '2020/21', '2023/24'],
    repeated: [{ employer: 'bc-hydro', year: '2020/21', repeats: '2017/18', rows: 20, same: 20 }],
    employers: [{ slug: 'bc-hydro', names: ['BC Hydro'], sector: 'Crown corporations', body: 'bc-hydro', counts: [1, 0, 0], rows: [['Old, A', null, 90000, null, 0]] }] }
  const bytes = gzipSync(JSON.stringify(baseline))
  writeFileSync(join(research, 'baseline.json.gzip'), bytes)
  writeFileSync(join(research, 'baseline-manifest.json'), JSON.stringify({ file: 'baseline.json.gzip', sha256: sha256(bytes), repositoryCommit: 'fixture' }))
  const sourceDir = join(research, 'official'); mkdirSync(sourceDir)
  const data = gzipSync(JSON.stringify([['bc-hydro', 'New, Alice', null, 122528.25, 704.02, 189]]))
  writeFileSync(join(sourceDir, '2020-21.json.gzip'), data)
  const manifest = { sources: [{ id: 'official-2021', year: '2020/21', employerSlug: 'bc-hydro', scope: 'employee-remuneration', file: '2020-21.json.gzip', dataSha256: sha256(data), sourceUrl: 'https://example.test/2021.pdf', periodStart: '2020-04-01', periodEnd: '2021-03-31', rowCount: 1, totalRemuneration: 122528.25, totalDisclosedExpenses: 704.02, threshold: 75000, thresholdRule: 'at-least' }] }
  writeFileSync(join(sourceDir, 'sources.json'), JSON.stringify(manifest))
  const out = join(dir, 'published'); mkdirSync(out); writeFileSync(join(out, 'sentinel'), 'working site')
  const run = () => spawnSync(process.execPath, [resolve('scripts/build-salaries.mjs'), '--research', research, '--out', out], { encoding: 'utf8' })
  return { dir, research, sourceDir, manifest, out, run }
}
test('a corrupted official input cannot erase the previous published output', () => {
  const f = fixture()
  try {
    f.manifest.sources[0].dataSha256 = 'incorrect'
    writeFileSync(join(f.sourceDir, 'sources.json'), JSON.stringify(f.manifest))
    const result = f.run()
    assert.notEqual(result.status, 0)
    assert.match(result.stderr, /hash mismatch/)
    assert.equal(readFileSync(join(f.out, 'sentinel'), 'utf8'), 'working site')
  } finally { rmSync(f.dir, { recursive: true, force: true }) }
})
test('verified replacements restore quarantined years consistently in every view with row provenance', () => {
  const f = fixture()
  try {
    f.manifest.sources[0].publicWarning = 'Published expenses have an unresolved source subtotal difference.'
    writeFileSync(join(f.sourceDir, 'sources.json'), JSON.stringify(f.manifest))
    const result = f.run()
    assert.equal(result.status, 0, result.stderr)
    const employers = JSON.parse(readFileSync(join(f.out, 'employers/index.json')))
    const year = employers.years.indexOf('2020/21')
    assert.equal(employers.employers[0].counts[year], 1)
    assert.equal(employers.employers[0].coverage[year].status, 'available')
    assert.equal(employers.employers[0].coverage[year].thresholdComparison, '>=')
    assert.equal(employers.sources['official-2021'].thresholdComparison, '>=')
    assert.equal(employers.sources['official-2021'].publicWarning, f.manifest.sources[0].publicWarning)
    assert.equal(JSON.parse(readFileSync(join(f.out, 'people/index.json'))).sources['official-2021'].publicWarning, f.manifest.sources[0].publicWarning)
    assert.deepEqual(employers.employers[0].repeated, [])
    const atlas = JSON.parse(readFileSync(join(f.out, '2020-21/bc-hydro.json')))
    assert.deepEqual(atlas.rows[0], ['New, Alice', null, 122528.25, 704.02, 'official-2021', 189])
    const people = JSON.parse(gunzipSync(readFileSync(join(f.out, 'people/ne.json.gzip'))))
    assert.equal(people[0][5], year)
    assert.equal(people[0][6], 'official-2021')
    assert.equal(people[0][7], 189)
    const coverage = JSON.parse(readFileSync(join(f.out, 'coverage.json')))
    assert.equal(coverage.corrections[0].status, 'replaced-from-official-source')
    assert.equal(coverage.output.rows, 2)
    const again = f.run()
    assert.equal(again.status, 0, again.stderr)
    assert.equal(JSON.parse(readFileSync(join(f.out, 'coverage.json'))).output.rows, 2)
  } finally { rmSync(f.dir, { recursive: true, force: true }) }
})

test('a title keeps the median of every record where employers share a year, overall and by sector', () => {
  const f = fixture()
  try {
    // The employers' medians (150, 1000, 70) would give 150; the six records' own median is 125.
    const baseline = { provenance: { description: 'Fixture compiled input' }, years: ['2017/18', '2020/21', '2023/24'], repeated: [],
      employers: [
        { slug: 'city-of-a', names: ['City of A'], sector: 'Government', counts: [3, 0, 0], rows: [['A, One', 'Mayor', 100, null, 0], ['A, Two', 'Mayor', 150, null, 0], ['A, Three', 'Mayor', 200, null, 0]] },
        { slug: 'city-of-b', names: ['City of B'], sector: 'Government', counts: [1, 1, 0], rows: [['B, One', 'Mayor', 1000, null, 0], ['B, One', 'Mayor', 1100, null, 1]] },
        { slug: 'bc-hydro', names: ['BC Hydro'], sector: 'Crown corporations', body: 'bc-hydro', counts: [2, 0, 0], rows: [['H, One', 'Mayor', 60, null, 0], ['H, Two', 'Mayor', 80, null, 0]] }
      ] }
    const bytes = gzipSync(JSON.stringify(baseline))
    writeFileSync(join(f.research, 'baseline.json.gzip'), bytes)
    writeFileSync(join(f.research, 'baseline-manifest.json'), JSON.stringify({ file: 'baseline.json.gzip', sha256: sha256(bytes), repositoryCommit: 'fixture' }))
    rmSync(f.sourceDir, { recursive: true })
    const result = f.run()
    assert.equal(result.status, 0, result.stderr)
    const mayor = JSON.parse(gunzipSync(readFileSync(join(f.out, 'positions/ma.json.gzip')))).mayor
    // 2020/21 has one employer, and Crown corporations one in every year: their medians are the cells'.
    assert.deepEqual(mayor.medians.all, [[0, 125]])
    assert.deepEqual(mayor.medians.Municipalities, [[0, 175]])
    assert.equal(mayor.medians['Crown corporations'], undefined)
  } finally { rmSync(f.dir, { recursive: true, force: true }) }
})

test('a source-only future year appears as pending coverage without adding records', () => {
  const f = fixture()
  try {
    writeFileSync(join(f.research, 'source-backlog.json'), JSON.stringify({ sources: [{ id: 'found-2027', employerSlug: 'bc-hydro', year: '2026/27', sourceUrl: 'https://example.test/2027.pdf', status: 'source-found-awaiting-extraction' }] }))
    const result = f.run()
    assert.equal(result.status, 0, result.stderr)
    const employers = JSON.parse(readFileSync(join(f.out, 'employers/index.json')))
    const at = employers.years.indexOf('2026/27')
    assert.ok(at >= 0)
    const coverage = employers.employers[0].coverage[at]
    assert.equal(coverage.status, 'source-found')
    assert.equal(coverage.rows, 0)
    assert.deepEqual(coverage.sourceIds, [])
    assert.equal(coverage.sourceLeads[0].url, 'https://example.test/2027.pdf')
  } finally { rmSync(f.dir, { recursive: true, force: true }) }
})

test('a held multi-employer report retains held coverage', () => {
  const f = fixture()
  try {
    f.manifest.sources.push({ id: 'held-2025', year: '2024/25', employers: ['bc-hydro'], status: 'held-for-review', sourceUrl: 'https://example.test/2025.pdf', reason: 'Named totals do not reconcile.' })
    writeFileSync(join(f.sourceDir, 'sources.json'), JSON.stringify(f.manifest))
    const result = f.run()
    assert.equal(result.status, 0, result.stderr)
    const employers = JSON.parse(readFileSync(join(f.out, 'employers/index.json')))
    const coverage = employers.employers[0].coverage[employers.years.indexOf('2024/25')]
    assert.equal(coverage.status, 'excluded')
    assert.equal(coverage.rows, 0)
    assert.equal(coverage.sourceLeads[0].status, 'held-for-review')
    assert.match(coverage.notes[0], /reconcile/)
  } finally { rmSync(f.dir, { recursive: true, force: true }) }
})

test('unclassified official input is rejected before it can replace an employee partition', () => {
  const f = fixture()
  try {
    delete f.manifest.sources[0].scope
    writeFileSync(join(f.sourceDir, 'sources.json'), JSON.stringify(f.manifest))
    const result = f.run()
    assert.notEqual(result.status, 0)
    assert.match(result.stderr, /explicit disclosure scope is required/)
    assert.equal(readFileSync(join(f.out, 'sentinel'), 'utf8'), 'working site')
  } finally { rmSync(f.dir, { recursive: true, force: true }) }
})

test('source catalog decisions are per employer and period, including a partially held shared report', () => {
  const source = { id: 'hydro-2025', year: '2024/25', file: '2024-25.gzip', sourceUrl: 'https://example.test/shared.pdf', employers: [{ slug: 'sub-powertech-labs', rowCount: 179 }], deferredEmployers: [{ slug: 'bc-hydro', reason: 'Totals differ' }] }
  const backlog = { sources: [{ id: 'lead', employerSlug: 'sub-powertech-labs', year: '2024/25', sourceUrl: source.sourceUrl, status: 'source-found-awaiting-extraction' }, { id: 'stale', employerSlug: 'bcit', year: '2020/21', sourceUrl: 'https://example.test/stale.pdf', status: 'imported' }] }
  const catalog = sourceCatalog(backlog, [{ collection: 'hydro', manifest: { sources: [source] } }])
  assert.equal(catalog.length, 3)
  assert.equal(catalog.find((entry) => entry.employerSlug === 'sub-powertech-labs').status, 'imported')
  assert.equal(catalog.find((entry) => entry.employerSlug === 'bc-hydro').status, 'held-for-review')
  assert.equal(catalog.find((entry) => entry.employerSlug === 'bc-hydro').reason, 'Totals differ')
  assert.equal(catalog.find((entry) => entry.employerSlug === 'bcit').status, 'source-found-awaiting-extraction')
  assert.equal(hasLocatedSource(sourceLeadsFor(catalog, 'bc-hydro', '2024/25')), true)
  assert.deepEqual(sourceLeadsFor(catalog, 'sub-powertech-labs', '2024/25'), [])
  const preciseHold = sourceCatalog({}, [{ collection: 'municipal', manifest: { sources: [], unparsedSources: [
    { id: 'draft', employerSlug: 'city-of-west-kelowna', year: '2025', sourceUrl: 'https://example.test/draft.pdf', status: 'held-for-review', reason: 'Approval page is unsigned.', nextAction: 'Obtain the adopted report.' }
  ] } }])
  assert.equal(sourceLeadsFor(preciseHold, 'city-of-west-kelowna', '2025')[0].reason, 'Approval page is unsigned.')
  assert.equal(preciseHold[0].nextAction, 'Obtain the adopted report.')
})

test('partial executive imports cannot erase an employee disclosure without a reviewed scope decision', () => {
  const before = [{ slug: 'bcit', year: '2020/21' }]
  const after = [{ slug: 'bcit', year: '2020/21', sourceId: 'executives' }]
  assert.throws(() => validateReplacementScopes(before, after, { executives: { scope: 'executive-only' } }), /partial disclosure/)
  assert.doesNotThrow(() => validateReplacementScopes(before, after, { executives: { scope: 'employee-remuneration' } }))
  assert.doesNotThrow(() => validateReplacementScopes(before, after, { executives: { scope: 'executive-only' } }, [{ kind: 'replace-partition-scope', employer: 'bcit', year: '2020/21', sourceIds: ['executives'], reason: 'Reviewed replacement scope.' }]))
})

test('employee and elected cohorts in one report retain distinct source-catalog entries', () => {
  const shared = { employerSlug: 'city-of-prince-george', year: '2025', file: 'data.gzip', sourceUrl: 'https://example.test/sofi.pdf' }
  const sources = [{ ...shared, id: 'staff', category: 'employee-remuneration', rowCount: 531 }, { ...shared, id: 'council', category: 'elected-officials', rowCount: 9 }]
  const catalog = sourceCatalog({ sources: [{ ...shared, id: 'lead', file: undefined }] }, [{ collection: 'municipal', manifest: { sources } }])
  assert.equal(catalog.length, 2)
  assert.deepEqual(catalog.map((entry) => entry.acceptedSourceId).sort(), ['council', 'staff'])
  assert.deepEqual(catalog.map((entry) => entry.scope).sort(), ['elected-officials', 'employee-remuneration'])
})

test('incorrect expense totals reject an import before changing published data', () => {
  const f = fixture()
  try {
    f.manifest.sources[0].totalExpenses = 900
    writeFileSync(join(f.sourceDir, 'sources.json'), JSON.stringify(f.manifest))
    const result = f.run()
    assert.notEqual(result.status, 0)
    assert.match(result.stderr, /expenses total mismatch/)
    assert.equal(readFileSync(join(f.out, 'sentinel'), 'utf8'), 'working site')
  } finally { rmSync(f.dir, { recursive: true, force: true }) }
})
