// Audit acquisition coverage without counting dedicated collections as empty.
// Requires the baseline commit in the local git object store.
import { execFileSync } from 'node:child_process'
import { readFileSync, writeFileSync } from 'node:fs'
import { fileURLToPath } from 'node:url'
import { COLLECTED_BODIES, COLLECTED_SPECIMENS } from '../../../src/gallery/collectedData.js'

const root = new URL('../../../', import.meta.url)
const baselineCommit = '658a83af56e4b6ebaf38bb1a69812d6052ce4cc1'
const baselineCode = execFileSync('git', ['show', `${baselineCommit}:src/gallery/collectedData.js`], {
  cwd: fileURLToPath(root), maxBuffer: 8 * 1024 * 1024
})
const baseline = await import(`data:text/javascript;base64,${baselineCode.toString('base64')}`)
const register = JSON.parse(readFileSync(new URL('./source-register.json', import.meta.url), 'utf8'))
const hasOriginal = (body) => body.assets.some((asset) => asset.isVector && !asset.reconstruction)
const category = (body) => body.existingCollection ? 'dedicatedCollection'
  : hasOriginal(body) ? 'originalVectorHeld'
    : body.assets.length ? 'artworkWithoutOriginalVector' : 'noAcquiredArtwork'
const count = (bodies, programs) => ({
  totalBodies: bodies.length,
  ...Object.fromEntries(['originalVectorHeld', 'artworkWithoutOriginalVector', 'noAcquiredArtwork', 'dedicatedCollection']
    .map((key) => [key, bodies.filter((body) => category(body) === key).length])),
  bodyAssetFiles: bodies.reduce((sum, body) => sum + body.assets.length, 0),
  programAssetFiles: programs.reduce((sum, program) => sum + program.assets.length, 0)
})
const brief = (body) => ({ id: body.id, name: body.name, kind: body.kind })
const baselineMap = new Map(baseline.COLLECTED_BODIES.map((body) => [body.id, body]))
const audit = {
  title: 'Acquisition coverage and remaining original-vector gaps',
  researchDate: '2026-11-08', timeZone: 'America/Vancouver', baselineCommit,
  scope: 'The 183 acquisition body records, with five dedicated collections classified separately. Program timelines and individual historical design gaps are not equivalent to inventory bodies.',
  countingRule: 'A verified original-vector asset has isVector true and reconstruction false/absent. existingCollection is classified first: dedicated collections are neither empty bodies nor a guarantee that every historical design has original artwork.',
  before: count(baseline.COLLECTED_BODIES, baseline.COLLECTED_SPECIMENS),
  after: count(COLLECTED_BODIES, COLLECTED_SPECIMENS),
  resolvedGeneralBodyGaps: COLLECTED_BODIES
    .filter((body) => !body.existingCollection && hasOriginal(body) && !hasOriginal(baselineMap.get(body.id)))
    .map(brief),
  dedicatedCollectionImprovements: [
    { id: 'bclc', change: 'Three original older-palette specimens added beside the reconstructed recolour; all in the documented 2008-era group.' },
    { id: 'worksafebc', change: 'Three original specimens added: a newly represented distressed WorkSafe design and two black/orange specimens. WorkSafeBC is a program record outside the 183-body acquisition inventory.' }
  ],
  newVectorFiles: register.assets.map(({ id, bodyId, file }) => ({ id, bodyId, file })),
  remainingWithArtworkButNoOriginalVector: COLLECTED_BODIES
    .filter((body) => category(body) === 'artworkWithoutOriginalVector').map(brief),
  noAcquiredArtwork: COLLECTED_BODIES.filter((body) => category(body) === 'noAcquiredArtwork').map(brief),
  dedicatedCollections: COLLECTED_BODIES.filter((body) => body.existingCollection)
    .map((body) => ({ ...brief(body), collectionId: body.existingCollection.collection })),
  limitation: 'This audit inventories files and declared provenance. It does not establish that an empty body used a distinct logo, that all existing dedicated-collection artwork is original vector, or that any unresolved original is unavailable elsewhere.'
}
const content = `${JSON.stringify(audit, null, 2)}\n`
const output = new URL('./gap-audit.json', import.meta.url)
if (process.argv.includes('--check')) {
  if (readFileSync(output, 'utf8') !== content) throw new Error('Gap audit differs from current acquisition data')
} else {
  writeFileSync(output, content)
}
console.log(JSON.stringify({ before: audit.before, after: audit.after, newFiles: audit.newVectorFiles.length, resolved: audit.resolvedGeneralBodyGaps.map((body) => body.id) }, null, 2))
