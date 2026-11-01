#!/usr/bin/env node
// No network calls. Import a supplied/authorized snapshot and retain its provenance.
import { readFileSync, mkdirSync, writeFileSync, renameSync, rmSync } from 'node:fs'
import { resolve, dirname, extname } from 'node:path'
import { fileURLToPath } from 'node:url'
import {
  normalizeSunshineSnapshot, parseSunshineCsv, parseSunshineEmployerHtml,
  sunshineSnapshotToCsv, sunshineInputSha256
} from './lib/sunshine-lists.mjs'

const usage = `Import an authorized local SunshineLists snapshot (no network access).

Usage:
  node scripts/import-sunshine-snapshot.mjs --input INPUT --out OUTPUT.json [options]

Options:
  --format json|csv|html   Defaults to input extension.
  --metadata SOURCE.json  Required for CSV/HTML: source provenance object.
  --csv OUTPUT.csv        Also write normalized aggregate/employer-year CSV.
  --help                  Show this message.

JSON uses {version:1, source:{url,retrievedAt,collectionMethod,complete:false,
expectedEmployerCount:null,notes:[]}, employers:[{name,url,years:[{year,
recordCount,periodType:'unknown'}]}]}.

CSV requires name,url,year,recordCount. Blank counts mean unknown, not zero.
Saved HTML requires metadata.employerName and extracts only explicit page
summary totals/ranges. It does not synthesize annual records from a range.
Directory completeness requires reconciled directory-page receipts; partial
search results and a complete:true flag alone are not sufficient.
`

const parseArgs = (args) => {
  const options = {}
  for (let index = 0; index < args.length; index += 1) {
    const arg = args[index]
    if (arg === '--help') { options.help = true; continue }
    if (!['--input', '--out', '--metadata', '--format', '--csv'].includes(arg)) throw new Error(`Unknown argument: ${arg}`)
    if (!args[index + 1] || args[index + 1].startsWith('--')) throw new Error(`Missing value for ${arg}`)
    if (options[arg.slice(2)]) throw new Error(`Repeated argument: ${arg}`)
    options[arg.slice(2)] = args[++index]
  }
  return options
}

const atomicWrite = (path, content) => {
  const target = resolve(path)
  mkdirSync(dirname(target), { recursive: true })
  const temporary = `${target}.${process.pid}.tmp`
  try { writeFileSync(temporary, content); renameSync(temporary, target) } finally { rmSync(temporary, { force: true }) }
}

export function main (args = process.argv.slice(2)) {
  const options = parseArgs(args)
  if (options.help) { process.stdout.write(usage); return null }
  if (!options.input || !options.out) throw new Error('--input and --out are required; see --help')
  const inputPath = resolve(options.input)
  const outputPath = resolve(options.out)
  if (inputPath === outputPath || (options.csv && resolve(options.csv) === inputPath)) throw new Error('Output must not overwrite the source input')
  if (options.csv && resolve(options.csv) === outputPath) throw new Error('JSON and CSV outputs must have different paths')
  if (options.metadata && [outputPath, options.csv && resolve(options.csv)].includes(resolve(options.metadata))) throw new Error('Output must not overwrite source metadata')
  const bytes = readFileSync(inputPath)
  const raw = bytes.toString('utf8').replace(/^\uFEFF/, '')
  const extension = extname(inputPath).slice(1).toLowerCase()
  const format = options.format ?? (extension === 'htm' ? 'html' : extension)
  const metadata = options.metadata ? JSON.parse(readFileSync(resolve(options.metadata), 'utf8')) : null
  let snapshot
  if (format === 'json') {
    if (metadata) throw new Error('JSON input already carries source metadata; --metadata is for CSV/HTML only')
    snapshot = normalizeSunshineSnapshot(JSON.parse(raw))
  } else if (format === 'csv' || format === 'html') {
    if (!metadata) throw new Error('--metadata is required for CSV/HTML input')
    snapshot = format === 'csv' ? parseSunshineCsv(raw, metadata) : parseSunshineEmployerHtml(raw, metadata)
  } else throw new Error(`Unsupported input format: ${format}`)
  snapshot.source.inputSha256 = sunshineInputSha256(bytes)
  const json = `${JSON.stringify(snapshot, null, 2)}\n`
  const csv = options.csv ? sunshineSnapshotToCsv(snapshot) : null
  // Finish parsing/validation before replacing any existing output.
  atomicWrite(outputPath, json)
  if (options.csv) atomicWrite(options.csv, csv)
  process.stdout.write(`${JSON.stringify({ output: outputPath, ...snapshot.summary }, null, 2)}\n`)
  return snapshot
}

if (process.argv[1] && resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  try { main() } catch (error) { process.stderr.write(`${error.message}\n`); process.exitCode = 1 }
}
