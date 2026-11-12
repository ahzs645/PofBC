// The brandkit brands for the Province's identities (brandkit/): every era builds into a folder
// brandkit itself validates, and packs into a pack brandkit can read back.
import { test } from 'node:test'
import assert from 'node:assert/strict'
import { spawnSync } from 'node:child_process'
import { existsSync, mkdtempSync, readFileSync, readdirSync, rmSync } from 'node:fs'
import { tmpdir } from 'node:os'
import { join } from 'node:path'
import { fileURLToPath } from 'node:url'
import { ERAS } from '../brandkit/eras.mjs'

const root = fileURLToPath(new URL('../', import.meta.url))
const ready = existsSync(join(root, 'vendor/brandkit/src/pack/cli.js'))

test('every era builds and packs', { skip: !ready && 'vendor/brandkit is not checked out', timeout: 300000 }, async () => {
  const work = mkdtempSync(join(tmpdir(), 'pofbc-brandkit-'))
  try {
    const env = { ...process.env, BRANDKIT_OUT: join(work, 'brands'), BRANDKIT_PACKS: join(work, 'packs') }
    const result = spawnSync(process.execPath, [join(root, 'brandkit/scripts/pack.mjs')], { cwd: root, env, encoding: 'utf8' })
    assert.equal(result.status, 0, result.stderr || result.stdout)

    const { validateBrand } = await import('../vendor/brandkit/src/engine/brand.js')
    const { readPack, readBundle } = await import('../vendor/brandkit/src/pack/format.js')
    for (const [index, era] of ERAS.entries()) {
      const brand = JSON.parse(readFileSync(join(work, 'brands', era.id, 'brand.json'), 'utf8'))
      assert.equal(brand.id, era.id)
      assert.deepEqual(validateBrand(brand), [], era.id)
      assert.equal(brand.era.order, index + 1)
      const pack = await readPack(new Uint8Array(readFileSync(join(work, 'packs', `${era.id}.zip`))))
      assert.equal(pack.manifest.id, era.id)
    }
    const catalog = JSON.parse(readFileSync(join(work, 'packs/catalog.json'), 'utf8'))
    assert.deepEqual(catalog.packs.map((entry) => entry.id).sort(), ERAS.map((era) => era.id).sort())
    const bundle = await readBundle(new Uint8Array(readFileSync(join(work, 'packs/bc-province.bundle.zip'))))
    assert.equal(bundle.packs.length, ERAS.length)
    assert.ok(readdirSync(join(work, 'brands/bc-province-current/artwork/ministry-marks')).length > 100, 'published ministry marks')
  } finally {
    rmSync(work, { recursive: true, force: true })
  }
})

test('the engraved-arms era starts with the McCarthy card, every line a field', () => {
  const source = readFileSync(join(root, 'brandkit/scripts/eras/engraved-arms.mjs'), 'utf8')
  for (const id of ['name', 'title-1', 'title-2', 'title-3', 'telephone-line', 'city', 'province']) assert.match(source, new RegExp(`id: '${id}'`))
  assert.ok(existsSync(join(root, 'artwork/stationery/grace-mccarthy/grace-mccarthy-card-editable.svg')))
})
