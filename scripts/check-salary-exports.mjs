// Independently reconcile every published salary view against the normalized source schedules.
// Run after build:salaries. --write-inventory also refreshes the human-readable coverage table.
import assert from 'node:assert/strict'
import { readFileSync, readdirSync, writeFileSync } from 'node:fs'
import { gunzipSync } from 'node:zlib'
import { createHash } from 'node:crypto'
import { fileURLToPath } from 'node:url'
import { resolve, dirname, join } from 'node:path'
import { SALARY_YEARS, SALARY_INDEX, SALARY_SOURCES, SALARY_COVERAGE } from '../src/government/salaryIndex.js'

const root = resolve(dirname(fileURLToPath(import.meta.url)), '..')
const published = join(root, 'public/salaries')
const research = join(root, 'research/salaries')
const json = (file) => JSON.parse(readFileSync(file, 'utf8'))
const gzip = (file) => JSON.parse(gunzipSync(readFileSync(file)))
const cents = (amount) => Math.round(amount * 100)
const add = (map, key) => map.set(key, (map.get(key) ?? 0) + 1)
const consume = (map, key, context) => {
  const count = map.get(key) ?? 0
  assert.ok(count > 0, `${context}: unexpected or over-repeated row ${key}`)
  if (count === 1) map.delete(key)
  else map.set(key, count - 1)
}
const canonical = (slug) => employers.aliases?.[slug] ?? slug
const employers = json(join(published, 'employers/index.json'))
const people = json(join(published, 'people/index.json'))
const atlas = json(join(published, 'index.json'))
const audit = json(join(published, 'coverage.json'))
const years = employers.years
assert.deepEqual(people.years, years, 'People and employer year indices differ')
assert.deepEqual(atlas.years.map((year) => year.label), years, 'Atlas year indices differ')
assert.deepEqual(people.sources, employers.sources)
assert.deepEqual(atlas.sources, employers.sources)
assert.deepEqual(SALARY_YEARS, atlas.years, 'Generated atlas module has stale years')
assert.deepEqual(SALARY_INDEX, atlas.bodies, 'Generated atlas module has stale counts or metadata')
assert.deepEqual(SALARY_SOURCES, atlas.sources, 'Generated atlas module has stale sources')
assert.deepEqual(SALARY_COVERAGE, atlas.coverage, 'Generated atlas module has stale coverage')
assert.deepEqual(people.employers.map((entry) => entry[3]), employers.employers.map((entry) => entry.slug))

let totalRows = 0; let namedRows = 0; let officialRows = 0; let duplicateRows = 0
let availableEmployerYears = 0; let atlasFiles = 0
const named = new Map(); const official = new Map(); const bodyRows = new Map()
const employerFiles = new Set()
for (const employer of employers.employers) {
  const file = `${employer.slug}.json.gzip`
  employerFiles.add(file)
  const rows = gzip(join(published, 'employers', file))
  if (employer.body) assert.deepEqual(atlas.coverage[employer.body], employer.coverage, `Atlas coverage differs for ${employer.body}`)
  totalRows += rows.length
  const byYear = years.map(() => [])
  for (const row of rows) {
    const [name, position, pay, expenses, year, sourceId, page] = row
    assert.equal(row.length, 7, `${employer.slug}: row schema`)
    assert.ok(page === null || (Number.isInteger(page) && page > 0), `${employer.slug}: physical PDF page`)
    assert.ok(Number.isInteger(year) && year >= 0 && year < years.length, `${employer.slug}: year index`)
    assert.ok(employers.sources[sourceId], `${employer.slug}: missing source ${sourceId}`)
    assert.ok(Number.isFinite(pay) && (expenses === null || Number.isFinite(expenses)), `${employer.slug}: money`)
    byYear[year].push(row)
    const key = JSON.stringify([employer.slug, years[year], name, position, pay, expenses, sourceId, page])
    if (name !== null) { namedRows += 1; add(named, key) }
    if (employers.sources[sourceId].sourceKind !== 'compiled' && employers.sources[sourceId].scope !== 'compiled-unverified') { officialRows += 1; add(official, key) }
    if (employer.body) {
      const bodyKey = `${years[year]}|${employer.body}`
      if (!bodyRows.has(bodyKey)) bodyRows.set(bodyKey, [])
      bodyRows.get(bodyKey).push([name, position, pay, expenses, sourceId, page])
    }
  }
  for (const [year, rowsForYear] of byYear.entries()) {
    const coverage = employer.coverage[year]
    assert.equal(employer.counts[year], rowsForYear.length, `${employer.slug} ${years[year]}: count`)
    assert.equal(coverage.rows, rowsForYear.length)
    assert.equal(coverage.status === 'available', rowsForYear.length > 0)
    assert.equal(coverage.namedRows, rowsForYear.filter((row) => row[0] !== null).length)
    assert.equal(coverage.positions, rowsForYear.filter((row) => row[1]).length)
    const duplicates = rowsForYear.length - new Set(rowsForYear.map((row) => JSON.stringify(row.slice(0, 4)))).size
    assert.equal(coverage.duplicateRows, duplicates)
    duplicateRows += duplicates
    availableEmployerYears += rowsForYear.length > 0 ? 1 : 0
    assert.deepEqual(people.coverage[employer.slug][year], coverage)
  }
}
assert.deepEqual(new Set(readdirSync(join(published, 'employers')).filter((file) => file.endsWith('.gzip'))), employerFiles)

for (const [shard, expected] of Object.entries(people.shards)) {
  const rows = gzip(join(published, 'people', `${shard}.json.gzip`))
  assert.equal(rows.length, expected, `People shard ${shard}: count`)
  for (const row of rows) {
    const [name, position, pay, expenses, employer, year, sourceId, page] = row
    assert.equal(row.length, 8, `People shard ${shard}: row schema`)
    assert.ok(Number.isInteger(employer) && people.employers[employer], 'Unknown employer in person record')
    const slug = people.employers[employer][3]
    consume(named, JSON.stringify([slug, years[year], name, position, pay, expenses, sourceId, page]), `People shard ${shard}`)
  }
}
assert.equal(named.size, 0, 'Named employer rows are absent from the people index')
assert.deepEqual(new Set(readdirSync(join(published, 'people')).filter((file) => file.endsWith('.gzip'))), new Set(Object.keys(people.shards).map((shard) => `${shard}.json.gzip`)))

const atlasPaths = new Set()
for (const [body, periods] of Object.entries(atlas.bodies)) {
  for (const [yearSlug, summary] of Object.entries(periods)) {
    atlasPaths.add(`${yearSlug}/${body}.json`)
    const data = json(join(published, yearSlug, `${body}.json`))
    const key = `${data.year}|${body}`
    const expected = bodyRows.get(key)
    assert.ok(expected, `Unexpected atlas partition ${key}`)
    assert.deepEqual(data.rows.map((row) => JSON.stringify(row)).sort(), expected.map((row) => JSON.stringify(row)).sort(), `Atlas partition ${key}`)
    assert.equal(summary.count, expected.length)
    assert.equal(cents(summary.total), expected.reduce((sum, row) => sum + cents(row[2]), 0))
    assert.equal(summary.max, Math.max(...expected.map((row) => row[2])))
    bodyRows.delete(key); atlasFiles += 1
  }
}
assert.equal(bodyRows.size, 0, 'Employer rows are absent from the atlas')
const actualAtlasPaths = new Set()
for (const entry of readdirSync(published, { withFileTypes: true })) {
  if (!entry.isDirectory() || ['employers', 'people'].includes(entry.name)) continue
  assert.match(entry.name, /^\d{4}(?:-\d{2})?$/, 'Unexpected published salary directory')
  for (const file of readdirSync(join(published, entry.name))) actualAtlasPaths.add(`${entry.name}/${file}`)
}
assert.deepEqual(actualAtlasPaths, atlasPaths, 'Unindexed or missing atlas files')

let sourceFiles = 0
const consumedTravelCorrections = new Set()
for (const collection of json(join(research, 'collections.json')).collections) {
  const manifest = json(join(research, collection, 'sources.json'))
  for (const source of manifest.sources) {
    if (source.status && !['accepted', 'verified', 'imported'].includes(source.status)) continue
    if (!source.file) continue
    const file = join(research, collection, source.file)
    const hash = createHash('sha256').update(readFileSync(file)).digest('hex')
    assert.equal(hash, source.dataSha256 ?? source.normalizedSha256, `${source.id}: normalized hash`)
    const data = gzip(file)
    for (const [slug, name, position, pay, expenses, page] of Array.isArray(data) ? data : data.rows) {
      const correction = (audit.travelJoinCorrections ?? []).find((entry) => entry.employeeSourceId === source.id && entry.employerSlug === canonical(slug) && entry.year === (source.year ?? source.label) && entry.name === name && entry.pay === pay)
      if (correction) {
        assert.equal(expenses, correction.previousExpenses, 'Travel correction does not match the original normalized source')
        assert.equal(correction.replacementExpenses, null)
        assert.ok(employers.sources[correction.relatedOICSourceId], 'Travel correction lacks the recovered appointee source')
        assert.ok(!consumedTravelCorrections.has(correction), 'Travel correction matched multiple source rows')
        consumedTravelCorrections.add(correction)
      }
      consume(official, JSON.stringify([canonical(slug), source.year ?? source.label, name, position, pay, correction ? correction.replacementExpenses : expenses, source.id, page ?? null]), `Official schedule ${source.id}`)
    }
    sourceFiles += 1
  }
}
assert.equal(consumedTravelCorrections.size, (audit.travelJoinCorrections ?? []).length, 'Unapplied travel correction')
assert.equal(official.size, 0, 'Published official rows have no normalized source record')
assert.equal(audit.output.rows, totalRows)
assert.equal(audit.output.namedRows, namedRows)
assert.equal(audit.output.availableEmployerYears, availableEmployerYears)
assert.equal(audit.officialRows, officialRows)
assert.equal(audit.legacyRowsRetained + officialRows, totalRows)
assert.equal(audit.duplicates.reduce((sum, entry) => sum + entry.duplicateRows, 0), duplicateRows)
for (const entry of audit.sourceCatalog ?? []) {
  assert.ok(employers.employers.some((employer) => employer.slug === entry.employerSlug), `Source catalog: unknown employer ${entry.employerSlug}`)
  if (entry.status === 'imported') {
    assert.ok(employers.sources[entry.acceptedSourceId], `Source catalog: accepted source missing ${entry.acceptedSourceId}`)
    assert.equal(employers.sources[entry.acceptedSourceId].url, entry.url, 'Source catalog: accepted source URL differs')
    assert.equal(employers.sources[entry.acceptedSourceId].year, entry.year, 'Source catalog: accepted source year differs')
    const employer = employers.employers.find((employer) => employer.slug === entry.employerSlug)
    assert.ok(employer.coverage[years.indexOf(entry.year)]?.sourceIds.includes(entry.acceptedSourceId), 'Source catalog: imported employer/year has no published records from the claimed source')
  }
}

if (process.argv.includes('--write-inventory')) {
  const escape = (value) => String(value).replaceAll('|', '\\|').replaceAll('\n', ' ')
  const count = (value) => value.toLocaleString('en-CA')
  const ranges = (labels) => {
    const groups = []
    for (const label of labels) {
      const last = groups.at(-1)
      if (last && label.includes('/') === last.at(-1).includes('/') && Number(label.slice(0, 4)) === Number(last.at(-1).slice(0, 4)) + 1) last.push(label)
      else groups.push([label])
    }
    return groups.map((group) => group.length > 1 ? `${group[0]}–${group.at(-1)}` : group[0]).join(', ') || 'None'
  }
  const lines = [
    '# Employer coverage inventory', '',
    'Generated by `node scripts/check-salary-exports.mjs --write-inventory` after reconciling all employer, person and atlas exports against the accepted normalized sources.', '',
    `The dataset contains **${count(totalRows)} disclosure rows**, including **${count(officialRows)} rows from official schedules**, across **${employers.employers.length} employers** and **${availableEmployerYears} populated employer/years**. There are **${count(duplicateRows)} duplicate-looking extra rows** still flagged for source review. These are records, not verified distinct people or a workforce census.`, '',
    'The three count columns are the original compiled edition labels. Official replacements use their verified reporting periods; retained compiled rows still have unverified reporting periods. A dash means no imported records. “Held” means a source was found but its records failed the stated validation gate. Blank cells and missing years do not establish that an employer had no employees. The earliest and latest years in the catalog do not establish an employer’s dates of existence.', '',
    '“Official years” lists accepted source coverage, with the source-specific thresholds and cohorts in [coverage.json](../../public/salaries/coverage.json). It does not promise all payments or employees. Gaps are assessed within the employer’s corresponding calendar or fiscal periods; an incompatible period type is not an additional annual gap. Historical periods before 2006/07 require separate source work.', '',
    '| Employer | Sector | 2017/18 rows | 2020/21 rows | 2023/24 rows | Official years | Retained compiled years | Review flags |',
    '|---|---|---:|---:|---:|---|---|---|'
  ]
  for (const employer of [...employers.employers].sort((a, b) => a.names.at(-1).localeCompare(b.names.at(-1)))) {
    const officialYears = []; const compiledYears = []; const flags = []
    employer.coverage.forEach((entry, at) => {
      if (entry.status === 'excluded') flags.push(`${years[at]} held`)
      if (entry.status === 'source-found') flags.push(`${years[at]} source found; extraction pending`)
      if (entry.status !== 'available') return
      ;(entry.sourceIds.some((id) => employers.sources[id].sourceKind === 'compiled' || employers.sources[id].scope === 'compiled-unverified') ? compiledYears : officialYears).push(years[at])
      if (entry.scope === 'elected-officials') flags.push(`${years[at]} mayor/council only`)
      if (entry.scope === 'executive-only') flags.push(`${years[at]} executive only`)
      if (entry.duplicateRows) flags.push(`${years[at]}: ${entry.duplicateRows} duplicate-looking extras`)
    })
    const values = ['2017/18', '2020/21', '2023/24'].map((year) => employer.counts[years.indexOf(year)] || '—').map((value) => typeof value === 'number' ? count(value) : value)
    lines.push(`| ${escape(employer.names.at(-1))} | ${escape(employer.sector)} | ${values.join(' | ')} | ${ranges(officialYears)} | ${ranges(compiledYears)} | ${escape(flags.join('; ') || '—')} |`)
  }
  lines.push('', 'Source leads and extraction status: [source-backlog.json](source-backlog.json). Methodology and prioritized findings: [README.md](README.md).', '')
  writeFileSync(join(research, 'coverage-inventory.md'), lines.join('\n'))
  const catalog = audit.sourceCatalog ?? []
  const statuses = Object.fromEntries([...new Set(catalog.map((entry) => entry.status))].sort().map((status) => [status, catalog.filter((entry) => entry.status === status).length]))
  const sourceLines = ['# Salary source inventory', '',
    'Generated from accepted source manifests and the source backlog by `npm run build:salaries && npm run check:salaries`. A located document is not an accepted employee schedule. One report may be accepted for one employer and held for another.', '',
    '| Source status | Employer/source/period entries |', '|---|---:|',
    ...Object.entries(statuses).map(([status, total]) => `| ${status} | ${total} |`), '',
    '| Employer | Period | Status | Accepted rows | Source | Next action |', '|---|---|---|---:|---|---|',
    ...catalog.map((entry) => {
      const employer = employers.employers.find((item) => item.slug === entry.employerSlug)
      const title = escape(entry.title).replaceAll('[', '\\[').replaceAll(']', '\\]')
      const source = entry.url ? `[${title}](${entry.url.replaceAll(' ', '%20').replaceAll('(', '%28').replaceAll(')', '%29')})` : title
      return `| ${escape(employer?.names.at(-1) ?? entry.employerSlug)} | ${entry.year ?? 'Historical / multiple'} | ${entry.status} | ${entry.status === 'imported' && entry.rows != null ? count(entry.rows) : '—'} | ${source} | ${escape(entry.nextAction)} |`
    }), '',
    'Employers and periods without a source entry still require source discovery; see [coverage-inventory.md](coverage-inventory.md). Source metadata never invents employee records or establishes that an employer had no employees.', '']
  writeFileSync(join(research, 'source-inventory.md'), sourceLines.join('\n'))
}
console.log(JSON.stringify({ status: 'passed', rows: totalRows, namedRows, officialRows, retainedCompiledRows: totalRows - officialRows, employers: employers.employers.length, availableEmployerYears, atlasFiles, peopleShards: Object.keys(people.shards).length, sourceFiles, duplicateLookingExtras: duplicateRows }, null, 2))
