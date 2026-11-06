import { createHash } from 'node:crypto'
import { readFileSync, writeFileSync, mkdirSync } from 'node:fs'
import { dirname, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'

const root = resolve(dirname(fileURLToPath(import.meta.url)), '..')
// RFC 4180-style parser: preserve every source string, including blanks and suppression markers.
export function parseProfileCsv(text) {
  const rows = []; let row = [], cell = '', quoted = false
  text = text.replace(/^\uFEFF/, '')
  for (let i = 0; i < text.length; i++) {
    const ch = text[i]
    if (ch === '"') {
      if (quoted && text[i + 1] === '"') { cell += '"'; i++ }
      else quoted = !quoted
    } else if (!quoted && (ch === ',' || ch === '\n' || ch === '\r')) {
      row.push(cell); cell = ''
      if (ch !== ',') { rows.push(row); row = []; if (ch === '\r' && text[i + 1] === '\n') i++ }
    } else cell += ch
  }
  if (quoted) throw new Error('Unterminated quoted CSV field')
  if (cell || row.length) { row.push(cell); rows.push(row) }
  return rows
}
export function buildProfiles(repoRoot = root) {
  const dir = resolve(repoRoot, 'research/salaries/workforce/profiles')
  const manifest = JSON.parse(readFileSync(resolve(dir, 'manifest.json'), 'utf8'))
  const tables = [...manifest.sources].sort((a, b) => a.name.localeCompare(b.name)).map(source => {
    const bytes = readFileSync(resolve(dir, source.file))
    if (createHash('sha256').update(bytes).digest('hex') !== source.sha256) throw new Error(`Source checksum mismatch: ${source.name}`)
    const [columns, ...rows] = parseProfileCsv(bytes.toString('utf8'))
    if (rows.length !== source.rowCount || rows.some(row => row.length !== columns.length)) throw new Error(`Invalid CSV dimensions: ${source.name}`)
    return { ...source, yearLabel: source.name.slice(2, 6), tableType: source.name.slice(7), recordType: source.name.endsWith('_MinistryKey') ? 'ministry-lookup' : 'aggregate-profile', columns, rows }
  })
  if (tables.length !== 30 || tables.reduce((n, t) => n + t.rows.length, 0) !== 10435) throw new Error('Unexpected profile archive coverage')
  const data = { schemaVersion: 1, datasetType: 'aggregate-workforce-profiles', catalogueUrl: manifest.catalogueUrl, description: manifest.description, license: manifest.license, retrievedOn: manifest.retrievedOn, totalSourceRows: 10435, notes: [
    'Source table rows are aggregate observations or ministry lookups, never individual employee records.',
    'All cells preserve source strings. S, NA and empty fields are not zero; no suppressed values are reconstructed.',
    'Year labels identify profile editions. Historical comparison columns may refer to earlier years.',
    'Employee counts, percentages, comparators, hiring flows and ministry lookup records have different units and denominators. Do not sum across tables or overlapping groups.',
    'These profiles are separate from FOI average headcount and average salary, named compensation disclosures and fiscal-year FTE statistics.'
  ], tables }
  return { data, json: JSON.stringify(data) + '\n' }
}
export function runProfileBuild({ check = false, repoRoot = root } = {}) {
  const { data, json } = buildProfiles(repoRoot)
  const target = resolve(repoRoot, 'public/salaries/workforce-profiles.json')
  if (check) {
    if (readFileSync(target, 'utf8') !== json) throw new Error('Stale workforce-profiles.json')
  } else { mkdirSync(dirname(target), { recursive: true }); writeFileSync(target, json) }
  return `${check ? 'Checked' : 'Built'} ${data.tables.length} profile tables and ${data.totalSourceRows} source rows.`
}
if (process.argv[1] && resolve(process.argv[1]) === fileURLToPath(import.meta.url)) console.log(runProfileBuild({ check: process.argv.includes('--check') }))
