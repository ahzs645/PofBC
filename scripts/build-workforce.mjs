import { readFileSync, writeFileSync, mkdirSync } from 'node:fs'
import { dirname, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'
import { validateWorkforce, workforceCsv } from '../src/salaries/workforce.js'

const root = resolve(dirname(fileURLToPath(import.meta.url)), '..')

export function buildWorkforce(source) {
  const data = validateWorkforce(structuredClone(source))
  data.observations.sort((a, b) => a.populationId.localeCompare(b.populationId) || a.yearLabel.localeCompare(b.yearLabel))
  return { json: JSON.stringify(data, null, 2) + '\n', csv: workforceCsv(data) }
}

export function runWorkforceBuild({ check = false, repoRoot = root } = {}) {
  const source = JSON.parse(readFileSync(resolve(repoRoot, 'research/salaries/workforce/PSA-2024-42006.json'), 'utf8'))
  const output = buildWorkforce(source)
  const target = resolve(repoRoot, 'public/salaries')
  if (!check) mkdirSync(target, { recursive: true })
  for (const [extension, contents] of Object.entries(output)) {
    const path = resolve(target, `workforce.${extension}`)
    if (check) {
      if (readFileSync(path, 'utf8') !== contents) throw new Error(`Stale workforce.${extension}; run node scripts/build-workforce.mjs`)
    } else writeFileSync(path, contents)
  }
  return `${check ? 'Checked' : 'Built'} workforce JSON and CSV: 16 observations, 2 overlapping populations.`
}

if (process.argv[1] && resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  console.log(runWorkforceBuild({ check: process.argv.includes('--check') }))
}
