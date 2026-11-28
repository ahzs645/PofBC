// Dump the site's bodies (atlas, current, sub-agencies, local and related bodies) with their names,
// for matching transfer payees: node research/finance/scripts/dump_bodies.mjs <out.json>
// Run from the repository root.
import { writeFileSync } from 'node:fs'
import { pathToFileURL } from 'node:url'
import { resolve } from 'node:path'

const load = (path) => import(pathToFileURL(resolve(path)).href)
const { HISTORICAL_BODIES, SUB_AGENCIES, LOCAL_BODIES } = await load('src/government/historyData.js')
const { CURRENT_BODIES } = await load('src/government/currentData.js')
const { RELATED_BODIES } = await load('src/government/relatedBodies.js')

const namesOf = (body) => [body.name, body.shortName, ...(body.aliases ?? []), ...(body.names ?? []).map((each) => (typeof each === 'string' ? each : each?.name))]
  .filter((name) => typeof name === 'string' && name.trim())
const out = []
const seen = new Set()
for (const [source, list] of [['atlas', HISTORICAL_BODIES], ['current', CURRENT_BODIES], ['sub', SUB_AGENCIES], ['local', LOCAL_BODIES], ['related', RELATED_BODIES]]) {
  for (const body of list) {
    if (!body.id || seen.has(body.id)) continue
    seen.add(body.id)
    out.push({ source, id: body.id, kind: body.kind ?? body.type ?? null, names: [...new Set(namesOf(body))], established: body.established ?? null, ended: body.ended ?? null })
  }
}
writeFileSync(process.argv[2] ?? 'bodies.json', JSON.stringify(out))
console.error(`${out.length} bodies`)
