// Independent application/order audit; reads frozen inputs and writes only stdout.
import fs from 'node:fs'
import zlib from 'node:zlib'
import { createHash } from 'node:crypto'
import { dirname, join, resolve } from 'node:path'
import { fileURLToPath, pathToFileURL } from 'node:url'

const root = resolve(dirname(fileURLToPath(import.meta.url)), '../../../..')
const { applyCompiledReplacements } = await import(pathToFileURL(join(root, 'scripts/lib/salary-data.mjs')))
const sha = bytes => createHash('sha256').update(bytes).digest('hex')
const read = name => {
  const bytes = fs.readFileSync(join(root, name))
  return JSON.parse(name.endsWith('.gzip') ? zlib.gunzipSync(bytes) : bytes.toString('utf8'))
}
const snapshot = read('research/salaries/compiled-baseline.json.gzip')
const comparison = read('research/salaries/queue-completion-2026-11-01/integration/compiled-comparison.json')
const list = read('research/salaries/queue-completion-acquisition/sources.json').sources
const baseline = snapshot.employers.flatMap(employer => employer.rows.map(row => ({
  slug: employer.slug, name: row[0], position: row[1], pay: row[2], expenses: row[3],
  year: snapshot.years[row[4]], sourceId: 'compiled'
})))
const baselineObjects = new Set(baseline)
const sources = {}
const official = []
for (const id of ['queue-completion-providence-2023-24-employees', 'queue-completion-vch-2020-21-employees']) {
  const source = list.find(entry => entry.id === id)
  sources[id] = source
  const rows = read('research/salaries/queue-completion-acquisition/' + source.file)
  for (const row of rows) official.push({ slug: row[0], name: row[1], position: row[2], pay: row[3], expenses: row[4], year: source.year, sourceId: id })
}
const rule = comparison.compiledReplacements[0]
const selected = baseline.filter(row => row.slug === rule.employerSlug && row.year === rule.compiledYear)
const digest = sha(JSON.stringify(selected.map(row => [row.name, row.position, row.pay, row.expenses])))
if (digest !== '30818d02354445ba5d6cef95d80ddcbe644904ecfbe5f53d8027e3ff2939d55b' || digest !== rule.selectedRowsSha256) throw new Error('Independent selected-order hash mismatch')
const beforeVCH = baseline.filter(row => row.slug === 'vancouver-coastal-health' && row.year === '2020/21')
const applied = applyCompiledReplacements(baseline, official, structuredClone(sources), comparison.compiledReplacements)
const afterVCH = applied.rows.filter(row => row.slug === 'vancouver-coastal-health' && row.year === '2020/21')
if (applied.rows.length !== baseline.length - 3289 || sha(JSON.stringify(beforeVCH)) !== sha(JSON.stringify(afterVCH))) throw new Error('Replacement scope mismatch')
let failsClosed = false
try {
  const changed = structuredClone(sources)
  changed[rule.sourceIds[0]].sha256 = '0'.repeat(64)
  applyCompiledReplacements(baseline, official, changed, [rule])
} catch (error) {
  failsClosed = /original replacement source fingerprint changed/.test(error.message)
}
if (!failsClosed) throw new Error('Changed original PDF hash was not rejected')
const result = {
  baselineSnapshotRows: baseline.length, selectedProvidenceRows: selected.length,
  independentJSSelectedRowsSha256: digest, resultRows: applied.rows.length,
  removedRows: baseline.length - applied.rows.length,
  VCHBeforeRows: beforeVCH.length, VCHAfterRows: afterVCH.length,
  VCHAllRowsAndOrderRetained: sha(JSON.stringify(beforeVCH)) === sha(JSON.stringify(afterVCH)),
  VCHAllEightExecutivePositionsRetained: afterVCH.filter(row => row.position !== null).length === 8,
  unchangedDataWithChangedOriginalHashRejected: failsClosed,
  correctionKind: applied.corrections[0].kind,
  allUnselectedRowObjectsRetained: applied.rows.every(row => baselineObjects.has(row))
}
process.stdout.write(JSON.stringify(result, null, 2) + '\n')
