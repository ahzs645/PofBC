// Dump atlas bodies, related bodies and identity-register subjects to JSON for matching.
// Run from the repository root: node research/finance/public-accounts-23-1/scripts/dump_site.mjs site.json
import { writeFileSync } from 'fs'
import { pathToFileURL } from 'url'
import { resolve } from 'path'
const mod = (p) => import(pathToFileURL(resolve(p)).href)
const h = await mod('src/government/historyData.js')
const c = await mod('src/government/currentData.js')
const r = await mod('src/government/relatedBodies.js')
const gs = await mod('src/government/governmentSearch.js')
const ic = await mod('src/gallery/identityCoverage.js')
const nm = (x) => [x.name, x.shortName, x.title, ...(x.aliases || []), ...((x.names || []).map((n) => (typeof n === 'string' ? n : n && n.name)))].filter((v) => typeof v === 'string')
const out = []
for (const x of h.HISTORICAL_BODIES) out.push({ src: 'atlas:HISTORICAL_BODIES', id: x.id, kind: x.kind, names: nm(x), from: x.established, to: x.ended, current: x.current })
for (const x of c.CURRENT_BODIES) out.push({ src: 'atlas:CURRENT_BODIES', id: x.id, kind: x.kind, names: nm(x), from: x.established })
for (const x of h.SUB_AGENCIES) out.push({ src: 'atlas:SUB_AGENCIES', id: x.id, kind: x.type, names: nm(x), from: x.established, parent: x.parent })
for (const x of h.LOCAL_BODIES) out.push({ src: 'atlas:LOCAL_BODIES', id: x.id, kind: x.kind, names: nm(x), from: x.established, to: x.ended })
for (const x of r.RELATED_BODIES) out.push({ src: 'related:RELATED_BODIES', id: x.id, kind: x.kind, names: nm(x) })
const seen = new Set(out.map((o) => o.id))
for (const x of gs.buildSearchIndex()) if (!seen.has(x.id)) out.push({ src: 'atlas:searchIndex', id: x.id, kind: '', names: nm(x), from: x.year })
for (const x of ic.IDENTITY_COVERAGE || []) out.push({ src: 'identity:IDENTITY_COVERAGE', id: x.id, kind: x.kind, names: nm(x), family: x.family, state: x.state || x.status })
writeFileSync(process.argv[2] || 'site.json', JSON.stringify(out))
