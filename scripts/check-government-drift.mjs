import { readFileSync, existsSync, readdirSync } from 'node:fs'
import { spawnSync } from 'node:child_process'
// The research queue's batches are regenerated whole, so their set of files is compared too.
const batches = () => existsSync('research/queue/batches') ? readdirSync('research/queue/batches').sort().map((name) => `research/queue/batches/${name}`) : []
const fixed = ['src/government/historyData.js', 'src/government/eventsData.js', 'src/government/atlasData.js', 'src/government/researchData.js', 'research/sub-agencies/BRIEF.md', 'research/sub-agencies/TEMPLATE.json', 'research/queue/INDEX.md', 'research/queue/sub-agencies.json', ...['events', 'history', 'atlas'].map((name) => `research/audit/${name}-import.json`)]
const files = [...fixed, ...batches()]
const before = new Map(files.map((name) => [name, existsSync(name) ? readFileSync(name) : null]))
const result = spawnSync('npm', ['run', 'build:government'], { stdio: 'inherit', env: { ...process.env, GOVERNMENT_AS_OF: process.env.GOVERNMENT_AS_OF ?? '2026-09-30' } })
if (result.status !== 0) process.exit(result.status ?? 1)
const after = [...fixed, ...batches()]
const changed = [...new Set([...files, ...after])].filter((name) => !existsSync(name) || !before.get(name)?.equals(readFileSync(name)))
if (changed.length) { console.error(`Government outputs need rebuilding:\n${changed.join('\n')}`); process.exit(1) }
console.log('Government outputs reproduce byte-for-byte')
